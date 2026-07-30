"""
NuruCare - Database Connection
==============================

Supports both Supabase and local PostgreSQL.
Use local PostgreSQL for Dockerized development and Supabase for hosted deployments.
"""

from __future__ import annotations

import hashlib
import os
import threading
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg.types.json import Json
from supabase import Client, create_client

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nurucare:nurucare@db:5432/nurucare")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    raise TypeError(f"Unsupported datetime value: {value!r}")


def _use_supabase() -> bool:
    return STORAGE_BACKEND == "supabase" and bool(SUPABASE_URL) and bool(SUPABASE_KEY)


_supabase: Optional[Client] = None
if _use_supabase():
    _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Database connected to Supabase")
else:
    print("[OK] Database connected to local PostgreSQL")


def _local_connection():
    # psycopg3 (the "psycopg" package) has a different API from psycopg2:
    # there is no psycopg.extras module, no RealDictCursor class, and
    # connect() takes row_factory instead of cursor_factory. row_factory is
    # set once here at the connection level, so every cursor opened from
    # this connection (connection.cursor() / conn.cursor(), ~30 call sites
    # throughout this file) automatically yields dict-like rows exactly as
    # RealDictCursor used to — no per-call-site changes needed.
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def _ensure_local_schema() -> None:
    schema_sql = """
    CREATE EXTENSION IF NOT EXISTS pgcrypto;

    CREATE TABLE IF NOT EXISTS users (
      user_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      username varchar(50) NOT NULL UNIQUE,
      email varchar(255) NOT NULL UNIQUE,
      password_hash varchar(255) NOT NULL,
      full_name varchar(255),
      role varchar(20) NOT NULL CHECK (role in ('patient', 'nurse', 'admin')),
      gender varchar(20),
      institution_name varchar(255),
      institution_address text,
      is_verified boolean NOT NULL DEFAULT false,
      is_active boolean NOT NULL DEFAULT true,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    DO $$ BEGIN
      ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;
    EXCEPTION WHEN duplicate_column THEN NULL; END $$;

    CREATE TABLE IF NOT EXISTS profiles (
      profile_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id uuid REFERENCES users(user_id) ON DELETE CASCADE,
      age int NOT NULL,
      systolic_bp int NOT NULL,
      diastolic_bp int NOT NULL,
      smoking boolean NOT NULL DEFAULT false,
      migraine_type varchar(50) NOT NULL DEFAULT 'none',
      breastfeeding boolean NOT NULL DEFAULT false,
      postpartum_weeks int,
      last_period_date date,
      duration_pref varchar(50),
      side_effects jsonb,
      sync_token_hash varchar(255),
      restricted_methods jsonb,
      allowed_methods jsonb,
      explanations jsonb,
      confidence_score numeric(5,2),
      intake_channel varchar(20) NOT NULL DEFAULT 'web',
      created_at timestamptz NOT NULL DEFAULT now()
    );

    DO $$ BEGIN
      ALTER TABLE profiles ADD COLUMN IF NOT EXISTS intake_channel varchar(20) NOT NULL DEFAULT 'web';
    EXCEPTION WHEN duplicate_column THEN NULL; END $$;

    CREATE TABLE IF NOT EXISTS partner_sync (
      sync_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      profile_id uuid REFERENCES profiles(profile_id) ON DELETE CASCADE,
      sync_token_hash varchar(255) NOT NULL,
      expires_at timestamptz NOT NULL,
      used boolean NOT NULL DEFAULT false,
      created_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS nurse_sessions (
      session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      profile_id uuid REFERENCES profiles(profile_id) ON DELETE CASCADE,
      access_code varchar(6) NOT NULL,
      expires_at timestamptz NOT NULL,
      used boolean NOT NULL DEFAULT false,
      force_expired boolean NOT NULL DEFAULT false,
      created_at timestamptz NOT NULL DEFAULT now()
    );

    DO $$ BEGIN
      ALTER TABLE nurse_sessions ADD COLUMN IF NOT EXISTS force_expired boolean NOT NULL DEFAULT false;
    EXCEPTION WHEN duplicate_column THEN NULL; END $$;

    CREATE TABLE IF NOT EXISTS content_items (
      content_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      content_type varchar(50) NOT NULL,
      item_key varchar(100) NOT NULL,
      content_data jsonb NOT NULL,
      version int NOT NULL DEFAULT 1,
      updated_by uuid REFERENCES users(user_id),
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE (content_type, item_key)
    );

    CREATE TABLE IF NOT EXISTS ussd_sessions (
      ussd_session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      external_session_id varchar(255),
      phone_number varchar(50),
      service_code varchar(50),
      status varchar(20) NOT NULL DEFAULT 'active',
      steps_completed int NOT NULL DEFAULT 0,
      profile_id uuid REFERENCES profiles(profile_id) ON DELETE SET NULL,
      created_at timestamptz NOT NULL DEFAULT now(),
      completed_at timestamptz
    );

    CREATE INDEX IF NOT EXISTS idx_profiles_age ON profiles(age);
    CREATE INDEX IF NOT EXISTS idx_profiles_intake_channel ON profiles(intake_channel);
    CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
    CREATE INDEX IF NOT EXISTS idx_partner_sync_expires_at ON partner_sync(expires_at);
    CREATE INDEX IF NOT EXISTS idx_nurse_sessions_expires_at ON nurse_sessions(expires_at);
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
    CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
    CREATE INDEX IF NOT EXISTS idx_content_items_type ON content_items(content_type);
    CREATE INDEX IF NOT EXISTS idx_ussd_sessions_status ON ussd_sessions(status);
    CREATE INDEX IF NOT EXISTS idx_ussd_sessions_created_at ON ussd_sessions(created_at);
    """

    with _local_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)
        connection.commit()


def create_user(
    username: str,
    email: str,
    password_hash: str,
    full_name: Optional[str] = None,
    role: str = "patient",
    gender: Optional[str] = None,
    institution_name: Optional[str] = None,
    institution_address: Optional[str] = None,
    is_active: bool = True
) -> dict:
    """Create a user. `is_active` defaults to True (patients, admin-created nurses,
    CLI-created admins are all usable immediately). Self-signup nurse accounts pass
    is_active=False explicitly — the account exists but cannot log in
    (login()/nurse_login() both reject inactive accounts) until an admin flips it
    active via the admin panel's existing Activate/Deactivate control."""
    if _use_supabase():
        try:
            payload = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name,
                "role": role,
                "gender": gender,
                "institution_name": institution_name,
                "institution_address": institution_address,
                "is_active": is_active
            }
            result = _supabase.table("users").insert(payload).execute()
            print(f"[OK] Supabase: Created user {username}")
            return {"success": True, "user_id": result.data[0]["user_id"]}
        except Exception as exc:
            print(f"[ERROR] Supabase error: {exc}")
            return {"success": False, "error": str(exc)}
    try:
        sql = """
            INSERT INTO users (
                username, email, password_hash, full_name, role, gender, 
                institution_name, institution_address, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id;
        """
        params = (
            username, email, password_hash, full_name, role, gender,
            institution_name, institution_address, is_active
        )
        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                user_id = cursor.fetchone()["user_id"]
            connection.commit()
        print(f"[OK] Local DB: Created user {username}")
        return {"success": True, "user_id": str(user_id)}
    except Exception as exc:
        print(f"[ERROR] Local DB error: {exc}")
        return {"success": False, "error": str(exc)}


def get_user_by_username(username: str) -> dict:
    if _use_supabase():
        try:
            result = _supabase.table("users").select("*").eq("username", username).execute()
            if not result.data:
                return {"success": False, "error": "User not found"}
            return {"success": True, "user": result.data[0]}
        except Exception as exc:
            print(f"[ERROR] Supabase error: {exc}")
            return {"success": False, "error": str(exc)}
    try:
        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                row = cursor.fetchone()
        if not row:
            return {"success": False, "error": "User not found"}
        return {"success": True, "user": row}
    except Exception as exc:
        print(f"[ERROR] Local DB error: {exc}")
        return {"success": False, "error": str(exc)}

def get_user_by_email(email: str) -> dict:
    if _use_supabase():
        try:
            result = _supabase.table("users").select("*").eq("email", email).execute()
            if not result.data:
                return {"success": False, "error": "User not found"}
            return {"success": True, "user": result.data[0]}
        except Exception as exc:
            print(f"[ERROR] Supabase error: {exc}")
            return {"success": False, "error": str(exc)}
    try:
        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                row = cursor.fetchone()
        if not row:
            return {"success": False, "error": "User not found"}
        return {"success": True, "user": row}
    except Exception as exc:
        print(f"[ERROR] Local DB error: {exc}")
        return {"success": False, "error": str(exc)}

if not _use_supabase():
    try:
        _ensure_local_schema()
    except Exception as e:
        print(f"[WARNING] Could not connect to PostgreSQL database: {e}")
        print("[WARNING] Database features will not be available, but app will still start")


def _auto_seed_demo_nurses() -> None:
    """Seed demo nurse accounts into users table (DEMO_MODE only, idempotent).

    Run once at import time regardless of backend (Supabase or local PG).
    Silent skip when DEMO_MODE is off or the rows already exist. Uses the
    real create_user → hash_password chain so bcrypt hashes are generated
    with correct rounds for the environment.
    """
    import os
    demo_mode = os.getenv("DEMO_MODE", "").lower() in ("1", "true", "yes", "on")
    if not demo_mode:
        return
    try:
        from auth import hash_password
    except Exception:
        return
    seed = [
        dict(username="nurse.demo", email="nurse.demo@nurucare.example",
             password="NuruCare2026", full_name="Demo Nurse", role="nurse",
             institution_name="NuruCare Demo Clinic",
             institution_address="123 Wellness Ave, Nairobi"),
        dict(username="dr.alex", email="dr.alex@nurucare.example",
             password="NuruCare2026", full_name="Dr. Alex Nuru", role="nurse",
             institution_name="NuruCare Regional Hospital",
             institution_address="456 Care Blvd, Kisumu"),
    ]
    for entry in seed:
        try:
            ex = get_user_by_username(entry["username"])
            if ex["success"]:
                continue
            pw_hash = hash_password(entry["password"])
            create_user(
                username=entry["username"],
                email=entry["email"],
                password_hash=pw_hash,
                full_name=entry["full_name"],
                role=entry["role"],
                gender=None,
                institution_name=entry["institution_name"],
                institution_address=entry["institution_address"],
            )
            print(f"[seed] Created demo nurse account: {entry['username']}")
        except Exception as exc:
            print(f"[seed] Skipped {entry['username']}: {exc}")


try:
    _auto_seed_demo_nurses()
except Exception:
    pass


def get_supabase() -> Optional[Client]:
    return _supabase


def save_intake_data(session_id: str, intake_data: dict, user_id: Optional[str] = None):
    row = {
        "profile_id": session_id,
        "user_id": user_id,
        "age": intake_data["age"],
        "systolic_bp": intake_data.get("systolic_bp") or 0,
        "diastolic_bp": intake_data.get("diastolic_bp") or 0,
        "smoking": intake_data.get("smoking", False),
        "migraine_type": intake_data.get("migraine_type", "none"),
        "breastfeeding": intake_data.get("breastfeeding", False),
        "postpartum_weeks": intake_data.get("postpartum_weeks"),
        "last_period_date": intake_data.get("last_period_date"),
        "duration_pref": intake_data.get("duration_pref"),
        "side_effects": intake_data.get("side_effects"),
        "restricted_methods": intake_data.get("restricted_methods"),
        "allowed_methods": intake_data.get("allowed_methods"),
        "explanations": intake_data.get("explanations"),
        "confidence_score": intake_data.get("confidence_score"),
        "intake_channel": intake_data.get("intake_channel", "web"),
    }

    if _supabase:
        try:
            payload = {k: v for k, v in row.items() if v is not None}
            result = _supabase.table("profiles").upsert(payload).execute()
            profile_id = result.data[0]["profile_id"]
            print(f"[OK] Supabase: Saved intake for profile {profile_id}" + (f" (user_id={user_id})" if user_id else " (anonymous)"))
            return {"success": True, "profile_id": profile_id}
        except Exception as exc:
            print(f"[ERROR] Supabase error: {exc}")
            return {"success": False, "error": str(exc)}

    try:
        sql = """
            INSERT INTO profiles (
                profile_id, user_id, age, systolic_bp, diastolic_bp, smoking, migraine_type,
                breastfeeding, postpartum_weeks, last_period_date, duration_pref,
                side_effects, restricted_methods, allowed_methods, explanations,
                confidence_score, intake_channel
            ) VALUES (
                COALESCE(%(profile_id)s::uuid, gen_random_uuid()), %(user_id)s::uuid, %(age)s, %(systolic_bp)s,
                %(diastolic_bp)s, %(smoking)s, %(migraine_type)s, %(breastfeeding)s,
                %(postpartum_weeks)s, %(last_period_date)s, %(duration_pref)s,
                %(side_effects)s, %(restricted_methods)s, %(allowed_methods)s,
                %(explanations)s, %(confidence_score)s, %(intake_channel)s
            )
            ON CONFLICT (profile_id) DO UPDATE SET
                user_id = COALESCE(EXCLUDED.user_id, profiles.user_id),
                age = EXCLUDED.age,
                systolic_bp = EXCLUDED.systolic_bp,
                diastolic_bp = EXCLUDED.diastolic_bp,
                smoking = EXCLUDED.smoking,
                migraine_type = EXCLUDED.migraine_type,
                breastfeeding = EXCLUDED.breastfeeding,
                postpartum_weeks = EXCLUDED.postpartum_weeks,
                last_period_date = EXCLUDED.last_period_date,
                duration_pref = EXCLUDED.duration_pref,
                side_effects = EXCLUDED.side_effects,
                restricted_methods = EXCLUDED.restricted_methods,
                allowed_methods = EXCLUDED.allowed_methods,
                explanations = EXCLUDED.explanations,
                confidence_score = EXCLUDED.confidence_score,
                intake_channel = EXCLUDED.intake_channel,
                created_at = now()
            RETURNING profile_id;
        """
        params = {
            **row,
            "side_effects": Json(row["side_effects"]) if row["side_effects"] is not None else None,
            "restricted_methods": Json(row["restricted_methods"]) if row["restricted_methods"] is not None else None,
            "allowed_methods": Json(row["allowed_methods"]) if row["allowed_methods"] is not None else None,
            "explanations": Json(row["explanations"]) if row["explanations"] is not None else None,
        }
        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                profile_id = cursor.fetchone()["profile_id"]
            connection.commit()
        print(f"[OK] Local DB: Saved intake for profile {profile_id}" + (f" (user_id={user_id})" if user_id else " (anonymous)"))
        return {"success": True, "profile_id": str(profile_id)}
    except Exception as exc:
        print(f"[ERROR] Local DB error: {exc}")
        return {"success": False, "error": str(exc)}


def save_session_key(session_key: str, profile_id: str):
    """Save nurse session key profile_id must already exist in profiles table"""
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    if _supabase:
        try:
            _supabase.table("nurse_sessions").insert({
                "profile_id": profile_id,
                "access_code": session_key,
                "expires_at": expires_at,
            }).execute()
            return {"success": True}
        except Exception as exc:
            print(f"[ERROR] Supabase error (session key): {exc}")
            return {"success": False, "error": str(exc)}

    try:
        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO nurse_sessions (profile_id, access_code, expires_at) VALUES (%s, %s, %s)",
                    (profile_id, session_key, expires_at),
                )
            connection.commit()
        return {"success": True}
    except Exception as exc:
        print(f"[ERROR] Local DB error (session key): {exc}")
        return {"success": False, "error": str(exc)}


def save_sync_token(token: str, from_profile_id: str):
    """Save partner sync token linked to a real profile_id"""
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    token_hash = _hash_token(token)
    if _supabase:
        try:
            _supabase.table("partner_sync").insert({
                "sync_token_hash": token_hash,
                "expires_at": expires_at,
                "profile_id": from_profile_id,
            }).execute()
            return {"success": True}
        except Exception as exc:
            print(f"[ERROR] Supabase error (sync token): {exc}")
            return {"success": False, "error": str(exc)}

    try:
        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO partner_sync (profile_id, sync_token_hash, expires_at) VALUES (%s, %s, %s)",
                    (from_profile_id, token_hash, expires_at),
                )
            connection.commit()
        return {"success": True}
    except Exception as exc:
        print(f"[ERROR] Local DB error (sync token): {exc}")
        return {"success": False, "error": str(exc)}


def verify_session_key(session_key: str):
    try:
        if _supabase:
            result = _supabase.table("nurse_sessions") \
                .select("profile_id, expires_at, used, force_expired") \
                .eq("access_code", session_key) \
                .eq("used", False) \
                .execute()
            if not result.data:
                return {"success": False, "error": "Invalid or expired session key"}
            row = result.data[0]
            if row.get("force_expired"):
                return {"success": False, "error": "Session key revoked by admin"}
            expires_at = _parse_datetime(row["expires_at"])
            if expires_at < datetime.now(timezone.utc):
                return {"success": False, "error": "Session key expired"}
            _supabase.table("nurse_sessions").update({"used": True}).eq("access_code", session_key).execute()
            return {"success": True, "patient_id": row["profile_id"]}

        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT profile_id, expires_at, used, force_expired FROM nurse_sessions WHERE access_code = %s AND used = false ORDER BY created_at DESC LIMIT 1",
                    (session_key,),
                )
                row = cursor.fetchone()
                if not row:
                    return {"success": False, "error": "Invalid or expired session key"}
                if row.get("force_expired"):
                    return {"success": False, "error": "Session key revoked by admin"}
                expires_at = _parse_datetime(row["expires_at"])
                if expires_at < datetime.now(timezone.utc):
                    return {"success": False, "error": "Session key expired"}
                cursor.execute("UPDATE nurse_sessions SET used = true WHERE access_code = %s", (session_key,))
            connection.commit()
        return {"success": True, "patient_id": str(row["profile_id"])}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════
# SINGLE SOURCE OF TRUTH — risk thresholds shared by both dashboards
# ═══════════════════════════════════════════════════════════════════
# These thresholds implement WHO MEC Category 3/4 rules and MUST be
# the only place they are defined. Never re-derive these inline.
#
# Shared by:
#   - get_dashboard_data()  (nurse dashboard aggregation)
#   - compute_safety_score() (patient dashboard safety score)
# ═══════════════════════════════════════════════════════════════════

def compute_risk_flags(profile: dict) -> dict:
    """Evaluate WHO-grounded risk flags from a profile dict.

    Returns a dict of boolean flags + aggregate risk band so every
    consumer (nurse dashboard, patient safety score, recommendation
    engine) agrees on categorisation.
    """
    age = int(profile.get("age") or 0)
    smoking = bool(profile.get("smoking"))
    migraine = profile.get("migraine_type") or "none"
    breastfeeding = bool(profile.get("breastfeeding"))
    systolic = int(profile.get("systolic_bp") or 0)
    diastolic = int(profile.get("diastolic_bp") or 0)

    # WHO MEC Category 4 (unacceptable risk) — must be surfaced everywhere
    who_cat4_age_smoking = smoking and age > 35
    who_cat4_migraine_aura = migraine == "with_aura"

    # WHO MEC Category 3 (advantages may not outweigh risks — clinical consult)
    who_cat3_migraine_no_aura = migraine == "without_aura"
    who_cat3_hypertension = systolic >= 140 or diastolic >= 90
    who_cat3_breastfeeding_early = breastfeeding  # method-specific, flag as caution

    # Aggregate bands used by UI visual layers
    is_high_risk = who_cat4_age_smoking or who_cat4_migraine_aura
    is_medium_risk = (
        who_cat3_migraine_no_aura
        or who_cat3_hypertension
        or (smoking and age <= 35)
    )

    # For the nurse dashboard "risk flag" counter — only WHO MEC Cat 4 counts
    has_cat4_flag = who_cat4_age_smoking or who_cat4_migraine_aura

    # Risk band strings matching the patient dashboard compute_safety_score output
    if is_high_risk:
        risk_level = "high"
    elif is_medium_risk:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        # Individual WHO-level flags
        "who_cat4_age_smoking": who_cat4_age_smoking,
        "who_cat4_migraine_aura": who_cat4_migraine_aura,
        "who_cat3_migraine_no_aura": who_cat3_migraine_no_aura,
        "who_cat3_hypertension": who_cat3_hypertension,
        "who_cat3_breastfeeding_early": who_cat3_breastfeeding_early,
        # Aggregates
        "is_high_risk": is_high_risk,
        "is_medium_risk": is_medium_risk,
        "has_cat4_flag": has_cat4_flag,
        "risk_level": risk_level,
        # Raw values for callers that want them for description text
        "_age": age,
        "_smoking": smoking,
        "_migraine": migraine,
        "_breastfeeding": breastfeeding,
        "_systolic": systolic,
        "_diastolic": diastolic,
    }


def get_dashboard_data():
    try:
        if _supabase:
            profiles = _supabase.table("profiles").select("*").order("created_at", desc=True).execute().data
        else:
            with _local_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM profiles ORDER BY created_at DESC")
                    profiles = cursor.fetchall()

        total = len(profiles)
        today = datetime.now(timezone.utc).date().isoformat()
        now = datetime.now(timezone.utc)
        daily = sum(1 for profile in profiles if str(profile.get("created_at", ""))[:10] == today)

        weekly = 0
        risk_flags = 0
        risk_band_counts = {"low": 0, "medium": 0, "high": 0}
        recommendation_counts = {}

        for profile in profiles:
            created_raw = str(profile.get("created_at", ""))
            try:
                created_dt = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                if (now - created_dt).days < 7:
                    weekly += 1
            except (ValueError, TypeError):
                pass

            risk = compute_risk_flags(profile)
            if risk["has_cat4_flag"]:
                risk_flags += 1
            risk_band_counts[risk["risk_level"]] += 1

            recommended_method = "Copper IUD" if not risk["_breastfeeding"] else "Progestin-only Pill"
            recommendation_counts[recommended_method] = recommendation_counts.get(recommended_method, 0) + 1

        buckets = {"15-19": 0, "20-24": 0, "25-29": 0, "30-34": 0, "35-39": 0, "40+": 0}
        for profile in profiles:
            age = profile.get("age") or 0
            if age < 20:
                buckets["15-19"] += 1
            elif age < 25:
                buckets["20-24"] += 1
            elif age < 30:
                buckets["25-29"] += 1
            elif age < 35:
                buckets["30-34"] += 1
            elif age < 40:
                buckets["35-39"] += 1
            else:
                buckets["40+"] += 1

        recent = []
        for profile in profiles[:10]:
            risk = compute_risk_flags(profile)
            age = risk["_age"]
            is_high = risk["is_high_risk"]
            is_medium = risk["is_medium_risk"]
            band_title = "High" if is_high else ("Medium" if is_medium else "Low")
            recent.append({
                "id": str(profile["profile_id"])[:8].upper(),
                "age": age,
                "status": "Flagged" if is_high else "Active",
                "riskLevel": band_title,
                "recommendation": "Copper IUD" if not risk["_breastfeeding"] else "Progestin-only Pill",
                "lastVisit": str(profile.get("created_at", ""))[:10],
            })

        risk_dist_fill = {"low": "hsl(174,52%,46%)", "medium": "hsl(43,74%,66%)", "high": "hsl(0,72%,60%)"}
        risk_dist_label = {"low": "Low", "medium": "Medium", "high": "High"}
        risk_distribution = []
        for band in ("low", "medium", "high"):
            count = risk_band_counts[band]
            pct = round((count / total) * 100) if total else 0
            risk_distribution.append({"name": risk_dist_label[band], "value": pct, "fill": risk_dist_fill[band]})

        recommendation_distribution = [
            {"name": name, "value": count} for name, count in sorted(recommendation_counts.items())
        ]

        return {"success": True, "data": {
            "activeConsultations": total,
            "riskFlags": risk_flags,
            "dailySessions": daily,
            "weeklySessions": weekly,
            "recentPatients": recent,
            "ageDemographics": [{"range": key, "count": value} for key, value in buckets.items()],
            "riskDistribution": risk_distribution,
            "recommendationDistribution": recommendation_distribution,
        }}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_profile_by_id(profile_id: str):
    try:
        if _supabase:
            result = _supabase.table("profiles").select("*").eq("profile_id", profile_id).execute()
            if not result.data:
                return {"success": False, "error": "Profile not found"}
            return {"success": True, "data": result.data[0]}

        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM profiles WHERE profile_id = %s", (profile_id,))
                row = cursor.fetchone()
        if not row:
            return {"success": False, "error": "Profile not found"}
        return {"success": True, "data": row}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def verify_sync_token(token: str):
    try:
        token_hash = _hash_token(token)
        if _supabase:
            result = _supabase.table("partner_sync") \
                .select("profile_id, expires_at, used") \
                .eq("sync_token_hash", token_hash) \
                .execute()
            if not result.data:
                return {"success": False, "error": "Invalid token"}
            row = result.data[0]
            if row["used"]:
                return {"success": False, "error": "Token already used"}
            expires_at = _parse_datetime(row["expires_at"])
            if expires_at < datetime.now(timezone.utc):
                return {"success": False, "error": "Token expired"}
            # Mark token as used
            _supabase.table("partner_sync").update({"used": True}).eq("sync_token_hash", token_hash).execute()
            return {"success": True, "from_user_id": row["profile_id"]}

        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT profile_id, expires_at, used FROM partner_sync WHERE sync_token_hash = %s ORDER BY created_at DESC LIMIT 1",
                    (token_hash,),
                )
                row = cursor.fetchone()
        if not row:
            return {"success": False, "error": "Invalid token"}
        if row["used"]:
            return {"success": False, "error": "Token already used"}
        expires_at = _parse_datetime(row["expires_at"])
        if expires_at < datetime.now(timezone.utc):
            return {"success": False, "error": "Token expired"}
        # Mark token as used
        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE partner_sync SET used = true WHERE sync_token_hash = %s", (token_hash,))
            connection.commit()
        return {"success": True, "from_user_id": str(row["profile_id"])}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def compute_safety_score(profile: dict) -> dict:
    """Compute a 0-100 safety/health score from profile flags + risk band.

    Uses the shared compute_risk_flags() helper so flag detection never
    drifts from the nurse dashboard aggregation. The weighted score
    deductions are specific to the patient safety-score layer but the
    boolean inputs come from the single source of truth.
    """
    risk = compute_risk_flags(profile)

    flags = []
    if risk["who_cat4_age_smoking"]:
        flags.append("Age >35 + smoking — WHO MEC Category 4 risk for combined methods")
    if risk["who_cat4_migraine_aura"]:
        flags.append("Migraine with aura — WHO MEC Category 4 risk for combined methods")
    if risk["who_cat3_migraine_no_aura"]:
        flags.append("Migraine without aura — monitor blood pressure closely with combined methods")
    if risk["who_cat3_breastfeeding_early"]:
        flags.append("Breastfeeding — only progestogen-only methods are recommended in the first 6 weeks")
    if risk["who_cat3_hypertension"]:
        flags.append("Elevated blood pressure — discuss options with a provider before starting combined methods")

    deductions = {
        "age_35_smoking": 40,
        "migraine_with_aura": 30,
        "migraine_without_aura": 8,
        "breastfeeding": 5,
        "hypertension": 12,
    }
    score = 100
    if risk["who_cat4_age_smoking"]:
        score -= deductions["age_35_smoking"]
    if risk["who_cat4_migraine_aura"]:
        score -= deductions["migraine_with_aura"]
    if risk["who_cat3_migraine_no_aura"]:
        score -= deductions["migraine_without_aura"]
    if risk["who_cat3_breastfeeding_early"]:
        score -= deductions["breastfeeding"]
    if risk["who_cat3_hypertension"]:
        score -= deductions["hypertension"]

    score = max(0, min(100, int(score)))

    return {"score": score, "risk_level": risk["risk_level"], "flags": flags}


def update_profile_fields(profile_id: str, fields: dict) -> dict:
    """Partial update of a profile row (e.g. side_effects).
    fields is a dict of column_name -> new_value. Supports Supabase + local PG.
    """
    allowed_cols = {
        "side_effects", "duration_pref", "last_period_date",
        "postpartum_weeks", "breastfeeding", "smoking",
        "migraine_type", "systolic_bp", "diastolic_bp", "age",
        "allowed_methods", "restricted_methods", "explanations",
        "confidence_score"
    }
    safe = {k: v for k, v in fields.items() if k in allowed_cols}
    if not safe:
        return {"success": False, "error": "No updatable fields provided"}

    try:
        if _supabase:
            # Serialize jsonb fields
            for col in ("side_effects", "allowed_methods", "restricted_methods", "explanations"):
                if col in safe and safe[col] is not None:
                    pass  # supabase client handles dict -> jsonb automatically
            result = (
                _supabase.table("profiles")
                .update(safe)
                .eq("profile_id", profile_id)
                .execute()
            )
            if not result.data or len(result.data) == 0:
                return {"success": False, "error": "Profile not found"}
            return {"success": True, "data": result.data[0]}

        assignments = []
        params = {"profile_id": profile_id}
        for col, val in safe.items():
            placeholder = f"%({col})s"
            if col in ("side_effects", "allowed_methods", "restricted_methods", "explanations"):
                assignments.append(f'{col} = {placeholder}::jsonb')
                params[col] = Json(val) if val is not None else None
            else:
                assignments.append(f'{col} = {placeholder}')
                params[col] = val

        sql = f'UPDATE profiles SET {", ".join(assignments)} WHERE profile_id = %(profile_id)s::uuid RETURNING *;'
        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone()
            connection.commit()
        if not row:
            return {"success": False, "error": "Profile not found"}
        return {"success": True, "data": row}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ================================================================
# ADMIN DASHBOARD — LIVE QUERIES
# ================================================================

def get_admin_overview_stats() -> dict:
    """Live platform stats for the admin landing tab.
    Every number is a real DB query.
    """
    try:
        if _supabase:
            users_data = _supabase.table("users").select("*").execute().data
            profiles_data = _supabase.table("profiles").select("*").execute().data
            try:
                ussd_data = _supabase.table("ussd_sessions").select("*").execute().data
            except Exception:
                ussd_data = []
        else:
            with _local_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users")
                    users_data = cur.fetchall()
                    cur.execute("SELECT * FROM profiles")
                    profiles_data = cur.fetchall()
                    try:
                        cur.execute("SELECT * FROM ussd_sessions")
                        ussd_data = cur.fetchall()
                    except Exception:
                        ussd_data = []

        total_patients = sum(1 for u in users_data if u.get("role") == "patient" and u.get("is_active", True))
        total_nurses = sum(1 for u in users_data if u.get("role") == "nurse" and u.get("is_active", True))
        total_admins = sum(1 for u in users_data if u.get("role") == "admin" and u.get("is_active", True))

        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        week_ago_str = week_ago.date().isoformat()

        new_this_week = 0
        for u in users_data:
            created = str(u.get("created_at", ""))[:10]
            if created >= week_ago_str:
                new_this_week += 1

        web_intake = sum(1 for p in profiles_data if p.get("intake_channel", "web") == "web")
        ussd_intake = sum(1 for p in profiles_data if p.get("intake_channel", "web") == "ussd")

        ussd_total_sessions = len(ussd_data)
        ussd_active = sum(1 for s in ussd_data if s.get("status") == "active")

        return {"success": True, "data": {
            "total_patients": total_patients,
            "total_nurses": total_nurses,
            "total_admins": total_admins,
            "new_signups_this_week": new_this_week,
            "channel_split": {
                "web": web_intake,
                "ussd": ussd_intake,
            },
            "ussd_sessions": {
                "total": ussd_total_sessions,
                "active": ussd_active,
                "tracked": True if ussd_data is not None else False,
            },
            "total_profiles": len(profiles_data),
        }}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_admin_signup_trend(days: int = 7) -> dict:
    """Daily signup counts for the last N days as real COUNT/GROUP BY."""
    try:
        result = []
        now = datetime.now(timezone.utc).date()
        if _supabase:
            users_data = _supabase.table("users").select("created_at, role").execute().data
            by_day = {}
            for u in users_data:
                day = str(u.get("created_at", ""))[:10]
                if day not in by_day:
                    by_day[day] = {"patient": 0, "nurse": 0, "admin": 0, "total": 0}
                role = u.get("role", "patient")
                if role in by_day[day]:
                    by_day[day][role] += 1
                by_day[day]["total"] += 1
            for i in range(days - 1, -1, -1):
                d = (now - timedelta(days=i)).isoformat()
                entry = by_day.get(d, {"patient": 0, "nurse": 0, "admin": 0, "total": 0})
                result.append({"date": d, **entry})
        else:
            with _local_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT
                            DATE(created_at) as signup_day,
                            COUNT(*) FILTER (WHERE role='patient') as patients,
                            COUNT(*) FILTER (WHERE role='nurse') as nurses,
                            COUNT(*) FILTER (WHERE role='admin') as admins,
                            COUNT(*) as total
                        FROM users
                        WHERE created_at >= NOW() - INTERVAL '%s days'
                        GROUP BY signup_day
                        ORDER BY signup_day ASC
                    """, (days,))
                    rows = cur.fetchall()
            by_day = {str(r["signup_day"]): {
                "patient": r["patients"], "nurse": r["nurses"],
                "admin": r["admins"], "total": r["total"]
            } for r in rows}
            for i in range(days - 1, -1, -1):
                d = (now - timedelta(days=i)).isoformat()
                entry = by_day.get(d, {"patient": 0, "nurse": 0, "admin": 0, "total": 0})
                result.append({"date": d, **entry})
        return {"success": True, "data": result}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ================================================================
# ADMIN — CONTENT MANAGER (content_items table + JSON file fallback)
# ================================================================

def list_content_items(content_type: Optional[str] = None) -> dict:
    """List content items, optionally filtered by type.
    Returns DB rows first; if DB empty, seed from JSON files in data/knowledge_base/."""
    from pathlib import Path
    import json as _json
    try:
        items = []
        if _supabase:
            q = _supabase.table("content_items").select("*")
            if content_type:
                q = q.eq("content_type", content_type)
            items = q.execute().data
        else:
            with _local_connection() as conn:
                with conn.cursor() as cur:
                    if content_type:
                        cur.execute("SELECT * FROM content_items WHERE content_type = %s ORDER BY item_key", (content_type,))
                    else:
                        cur.execute("SELECT * FROM content_items ORDER BY content_type, item_key")
                    items = cur.fetchall()

        if len(items) == 0 and not content_type:
            kb_dir = Path(__file__).parent.parent / "data" / "knowledge_base"
            seed_map = {
                "myths": kb_dir / "myths.json",
                "who_guidelines": kb_dir / "who_guidelines.json",
                "educational_content": kb_dir / "educational_content.json",
            }
            for ctype, fpath in seed_map.items():
                if fpath.exists():
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            raw = _json.load(f)
                    except Exception:
                        continue
                    arr_key = None
                    for k in ("myths", "guidelines", "methods"):
                        if k in raw and isinstance(raw[k], list):
                            arr_key = k
                            break
                    if arr_key is None:
                        continue
                    for idx, entry in enumerate(raw[arr_key]):
                        item_key = entry.get("id") or entry.get("method_id") or f"{ctype}_{idx}"
                        upsert_content_item(ctype, str(item_key), entry, None)
            return list_content_items(content_type)
        return {"success": True, "data": [dict(r) for r in items]}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_content_item(content_type: str, item_key: str) -> dict:
    try:
        if _supabase:
            r = _supabase.table("content_items").select("*").eq("content_type", content_type).eq("item_key", item_key).execute()
            if not r.data:
                return {"success": False, "error": "Not found"}
            return {"success": True, "data": r.data[0]}
        with _local_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM content_items WHERE content_type = %s AND item_key = %s", (content_type, item_key))
                row = cur.fetchone()
        if not row:
            return {"success": False, "error": "Not found"}
        return {"success": True, "data": dict(row)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def upsert_content_item(content_type: str, item_key: str, content_data: dict, updated_by: Optional[str]) -> dict:
    """Create or update a content item with version bump and audit fields."""
    try:
        existing = get_content_item(content_type, item_key)
        next_version = 1
        if existing["success"]:
            next_version = int(existing["data"].get("version", 0)) + 1

        if _supabase:
            payload = {
                "content_type": content_type,
                "item_key": item_key,
                "content_data": content_data,
                "version": next_version,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            if updated_by:
                payload["updated_by"] = updated_by
            r = _supabase.table("content_items").upsert(payload, on_conflict="content_type,item_key").execute()
            return {"success": True, "data": r.data[0]}

        with _local_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO content_items (content_type, item_key, content_data, version, updated_by, updated_at)
                    VALUES (%s, %s, %s::jsonb, %s, %s::uuid, now())
                    ON CONFLICT (content_type, item_key) DO UPDATE SET
                        content_data = EXCLUDED.content_data,
                        version = EXCLUDED.version,
                        updated_by = EXCLUDED.updated_by,
                        updated_at = now()
                    RETURNING *
                """, (content_type, item_key, Json(content_data), next_version, updated_by))
                row = cur.fetchone()
            conn.commit()
        return {"success": True, "data": dict(row)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def delete_content_item(content_type: str, item_key: str) -> dict:
    try:
        if _supabase:
            _supabase.table("content_items").delete().eq("content_type", content_type).eq("item_key", item_key).execute()
            return {"success": True}
        with _local_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM content_items WHERE content_type = %s AND item_key = %s", (content_type, item_key))
            conn.commit()
        return {"success": True}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ================================================================
# ADMIN — USER / ACCOUNT MANAGEMENT
# ================================================================

def list_all_users(role: Optional[str] = None, search: Optional[str] = None, limit: int = 200) -> dict:
    """List/search all users. Never returns password_hash."""
    try:
        rows = []
        if _supabase:
            q = _supabase.table("users").select("user_id, username, email, full_name, role, gender, institution_name, is_verified, is_active, created_at, updated_at")
            if role:
                q = q.eq("role", role)
            if search:
                q = q.or_(f"username.ilike.%{search}%,email.ilike.%{search}%,full_name.ilike.%{search}%")
            rows = q.limit(limit).order("created_at", desc=True).execute().data
        else:
            sql = """
                SELECT user_id, username, email, full_name, role, gender,
                       institution_name, is_verified, is_active, created_at, updated_at
                FROM users
                WHERE 1=1
            """
            params = []
            if role:
                sql += " AND role = %s"
                params.append(role)
            if search:
                sql += " AND (username ILIKE %s OR email ILIKE %s OR full_name ILIKE %s)"
                like = f"%{search}%"
                params.extend([like, like, like])
            sql += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            with _local_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
        return {"success": True, "data": [dict(r) for r in rows]}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_user_by_id_admin(user_id: str) -> dict:
    """Get a user record (without password_hash) by ID."""
    try:
        if _supabase:
            r = _supabase.table("users").select("user_id, username, email, full_name, role, gender, institution_name, institution_address, is_verified, is_active, created_at, updated_at").eq("user_id", user_id).execute()
            if not r.data:
                return {"success": False, "error": "User not found"}
            return {"success": True, "data": r.data[0]}
        with _local_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT user_id, username, email, full_name, role, gender,
                           institution_name, institution_address, is_verified, is_active,
                           created_at, updated_at
                    FROM users WHERE user_id = %s::uuid
                """, (user_id,))
                row = cur.fetchone()
        if not row:
            return {"success": False, "error": "User not found"}
        return {"success": True, "data": dict(row)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def update_user_role(user_id: str, new_role: str, actor_user_id: str) -> dict:
    """Promote/demote a user's role. Caller must already have verified actor is admin.

    "admin" is intentionally excluded from the allowed values: admin accounts are
    created exclusively via the `backend/scripts/create_admin.py` CLI bootstrap,
    never through this (or any other) HTTP-reachable endpoint. This is enforced at
    both the API layer (api/endpoints/admin.py) and here at the DB layer as
    defense in depth — a caller must not be able to reach admin promotion by any
    request path, authenticated or not.
    """
    if new_role not in ("patient", "nurse"):
        return {"success": False, "error": "Invalid role. Admin accounts can only be created via the CLI bootstrap script (backend/scripts/create_admin.py)."}
    try:
        if _supabase:
            r = _supabase.table("users").update({"role": new_role, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("user_id", user_id).execute()
            if not r.data:
                return {"success": False, "error": "User not found"}
            return {"success": True, "data": r.data[0]}
        with _local_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET role = %s, updated_at = now() WHERE user_id = %s::uuid RETURNING user_id, username, role, updated_at", (new_role, user_id))
                row = cur.fetchone()
            conn.commit()
        if not row:
            return {"success": False, "error": "User not found"}
        return {"success": True, "data": dict(row)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def toggle_user_active(user_id: str, is_active: bool) -> dict:
    """Deactivate or reactivate a user account."""
    try:
        if _supabase:
            r = _supabase.table("users").update({"is_active": is_active, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("user_id", user_id).execute()
            if not r.data:
                return {"success": False, "error": "User not found"}
            return {"success": True, "data": r.data[0]}
        with _local_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET is_active = %s, updated_at = now() WHERE user_id = %s::uuid RETURNING user_id, username, is_active, updated_at", (is_active, user_id))
                row = cur.fetchone()
            conn.commit()
        if not row:
            return {"success": False, "error": "User not found"}
        return {"success": True, "data": dict(row)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ================================================================
# ADMIN — SESSION & SYNC MONITORING
# ================================================================

def get_nurse_session_monitor() -> dict:
    """Active/expired nurse session counts + list of active codes."""
    try:
        now = datetime.now(timezone.utc)
        if _supabase:
            sessions = _supabase.table("nurse_sessions").select("*").order("created_at", desc=True).limit(200).execute().data
        else:
            with _local_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM nurse_sessions ORDER BY created_at DESC LIMIT 200")
                    sessions = cur.fetchall()

        active = 0
        expired = 0
        used = 0
        force_expired = 0
        recent = []
        for s in sessions:
            is_force = bool(s.get("force_expired", False))
            is_used = bool(s.get("used", False))
            if is_force:
                force_expired += 1
            if is_used:
                used += 1
            exp = s.get("expires_at")
            if isinstance(exp, str):
                exp = _parse_datetime(exp)
            if not exp:
                continue
            is_active = (not is_used) and (not is_force) and exp > now
            if is_active:
                active += 1
            elif not is_used:
                expired += 1
            recent.append({
                "session_id": str(s["session_id"]),
                "profile_id": str(s.get("profile_id"))[:8].upper() if s.get("profile_id") else None,
                "access_code": s["access_code"],
                "created_at": str(s.get("created_at", ""))[:16],
                "expires_at": str(s.get("expires_at", ""))[:16],
                "status": "active" if is_active else ("used" if is_used else ("force_expired" if is_force else "expired")),
            })
        return {"success": True, "data": {
            "active_count": active,
            "expired_count": expired,
            "used_count": used,
            "force_expired_count": force_expired,
            "sessions": recent[:50],
        }}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def force_expire_nurse_session(session_id: str) -> dict:
    """Admin force-expire a specific nurse access code."""
    try:
        if _supabase:
            r = _supabase.table("nurse_sessions").update({"force_expired": True}).eq("session_id", session_id).execute()
            if not r.data:
                return {"success": False, "error": "Session not found"}
            return {"success": True}
        with _local_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE nurse_sessions SET force_expired = true WHERE session_id = %s::uuid", (session_id,))
            conn.commit()
        return {"success": True}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_partner_sync_monitor() -> dict:
    """Partner sync token monitoring: active/expired/used counts + list."""
    try:
        now = datetime.now(timezone.utc)
        if _supabase:
            rows = _supabase.table("partner_sync").select("*").order("created_at", desc=True).limit(200).execute().data
        else:
            with _local_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM partner_sync ORDER BY created_at DESC LIMIT 200")
                    rows = cur.fetchall()

        active = 0
        expired = 0
        used = 0
        recent = []
        for s in rows:
            is_used = bool(s.get("used", False))
            exp = s.get("expires_at")
            if isinstance(exp, str):
                exp = _parse_datetime(exp)
            is_active = (not is_used) and exp and exp > now
            if is_active:
                active += 1
            elif not is_used:
                expired += 1
            else:
                used += 1
            recent.append({
                "sync_id": str(s["sync_id"]),
                "profile_id": str(s.get("profile_id"))[:8].upper() if s.get("profile_id") else None,
                "created_at": str(s.get("created_at", ""))[:16],
                "expires_at": str(s.get("expires_at", ""))[:16],
                "status": "active" if is_active else ("used" if is_used else "expired"),
            })
        return {"success": True, "data": {
            "active_count": active,
            "expired_count": expired,
            "used_count": used,
            "syncs": recent[:50],
        }}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ================================================================
# ADMIN — SYSTEM HEALTH
# ================================================================

def get_system_health_detail() -> dict:
    """Extended health: DB connectivity + API key status + entrypoint flags."""
    import os
    db_ok = True
    db_error = None
    try:
        if _supabase:
            _supabase.table("users").select("user_id").limit(1).execute()
        else:
            with _local_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
    except Exception as exc:
        db_ok = False
        db_error = str(exc)

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_configured = bool(gemini_key) and not gemini_key.startswith("sk-xxx") and not gemini_key.startswith("your-")

    engine_path = "hardcoded_fallback"
    try:
        from engine.guardrail import WHOMECGuardrail
        WHOMECGuardrail()
        engine_path = "engine_available_but_not_connected"
    except Exception:
        engine_path = "hardcoded_fallback"

    return {"success": True, "data": {
        "database": {
            "ok": db_ok,
            "backend": "supabase" if _use_supabase() else "local_postgres",
            "error": db_error,
        },
        "gemini_api": {
            "configured": gemini_configured,
            "key_present": bool(gemini_key),
            "redacted_key": (gemini_key[:4] + "..." + gemini_key[-4:]) if gemini_key else None,
        },
        "recommendation_engine": {
            "active_path": engine_path,
            "guardrail_loaded": engine_path != "hardcoded_fallback",
        },
        "entrypoint": {
            "backend_main": "main.py",
            "note": "FastAPI entrypoint; vite config is frontend-only.",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }}


# ================================================================
# RATE LIMITER — protects guessable 6-digit nurse access codes
# ================================================================

class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter.

    Used to prevent brute-force guessing of:
      - nurse_sessions.access_code (6-digit, 1M combinations → guessable)
      - partner_sync tokens (longer, but still low-entropy enough to be worth gating)

    Default config: 5 attempts per key per 60-second window.
    """

    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self._max = max_attempts
        self._window = timedelta(seconds=window_seconds)
        self._buckets: dict[str, deque] = {}
        self._lock = threading.Lock()

    def check_and_record(self, key: str) -> tuple[bool, int]:
        """Return (allowed, attempts_left_in_window)."""
        now = datetime.now(timezone.utc)
        cutoff = now - self._window
        with self._lock:
            dq = self._buckets.get(key)
            if dq is None:
                dq = deque()
                self._buckets[key] = dq
            while dq and dq[0] < cutoff:
                dq.popleft()
            if len(dq) >= self._max:
                return False, 0
            dq.append(now)
            return True, self._max - len(dq)


_NURSE_KEY_RL = SlidingWindowRateLimiter(max_attempts=5, window_seconds=60)
_SYNC_TOKEN_RL = SlidingWindowRateLimiter(max_attempts=10, window_seconds=60)


def rate_limited_verify_session_key(session_key: str) -> dict:
    """Wraps verify_session_key() with per-attempt rate limiting on the key.

    A 6-digit code has only 1M combinations — an attacker can enumerate it
    in ~10 minutes at 2k qps. Gating at 5 attempts/minute per code pushes
    that out to ~14 weeks (worst case) before the token expires anyway,
    which is the practical security level we need given the other
    mitigations (expiry, force_expire, single-use).
    """
    # Normalize / hash the input so the bucket key is deterministic but we
    # don't retain access codes in memory long-term.
    bucket = _hash_token(session_key or "")[:16]
    allowed, _left = _NURSE_KEY_RL.check_and_record(bucket)
    if not allowed:
        return {"success": False, "error": "Too many attempts. Wait 60 seconds and try again."}
    return verify_session_key(session_key)


def rate_limited_verify_sync_token(token: str) -> dict:
    """Wraps verify_sync_token() with rate limiting.

    Partner sync tokens are higher entropy (NX-XXX-XXX ~ 36^6 combos) so
    the limit is more permissive. Still, repeated failing requests should
    be throttled to stop dumb spray attacks.
    """
    bucket = _hash_token(token or "")[:16]
    allowed, _left = _SYNC_TOKEN_RL.check_and_record(bucket)
    if not allowed:
        return {"success": False, "error": "Too many attempts. Wait 60 seconds and try again."}
    return verify_sync_token(token)