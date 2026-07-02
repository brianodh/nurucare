"""
NuruCare - Database Connection
==============================

Supports both Supabase and local PostgreSQL.
Use local PostgreSQL for Dockerized development and Supabase for hosted deployments.
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json, RealDictCursor
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
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def _ensure_local_schema() -> None:
    schema_sql = """
    CREATE EXTENSION IF NOT EXISTS pgcrypto;

    CREATE TABLE IF NOT EXISTS profiles (
      profile_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
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
      created_at timestamptz NOT NULL DEFAULT now()
    );

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
      created_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_profiles_age ON profiles(age);
    CREATE INDEX IF NOT EXISTS idx_partner_sync_expires_at ON partner_sync(expires_at);
    CREATE INDEX IF NOT EXISTS idx_nurse_sessions_expires_at ON nurse_sessions(expires_at);
    """

    with _local_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)
        connection.commit()


if not _use_supabase():
    try:
        _ensure_local_schema()
    except Exception as e:
        print(f"[WARNING] Could not connect to PostgreSQL database: {e}")
        print("[WARNING] Database features will not be available, but app will still start")


def get_supabase() -> Optional[Client]:
    return _supabase


def save_intake_data(session_id: str, intake_data: dict):
    row = {
        "profile_id": session_id,
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
    }

    if _supabase:
        try:
            payload = {k: v for k, v in row.items() if v is not None}
            result = _supabase.table("profiles").upsert(payload).execute()
            profile_id = result.data[0]["profile_id"]
            print(f"[OK] Supabase: Saved intake for profile {profile_id}")
            return {"success": True, "profile_id": profile_id}
        except Exception as exc:
            print(f"[ERROR] Supabase error: {exc}")
            return {"success": False, "error": str(exc)}

    try:
        sql = """
            INSERT INTO profiles (
                profile_id, age, systolic_bp, diastolic_bp, smoking, migraine_type,
                breastfeeding, postpartum_weeks, last_period_date, duration_pref,
                side_effects, restricted_methods, allowed_methods, explanations,
                confidence_score
            ) VALUES (
                COALESCE(%(profile_id)s::uuid, gen_random_uuid()), %(age)s, %(systolic_bp)s,
                %(diastolic_bp)s, %(smoking)s, %(migraine_type)s, %(breastfeeding)s,
                %(postpartum_weeks)s, %(last_period_date)s, %(duration_pref)s,
                %(side_effects)s, %(restricted_methods)s, %(allowed_methods)s,
                %(explanations)s, %(confidence_score)s
            )
            ON CONFLICT (profile_id) DO UPDATE SET
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
        print(f"[OK] Local DB: Saved intake for profile {profile_id}")
        return {"success": True, "profile_id": str(profile_id)}
    except Exception as exc:
        print(f"[ERROR] Local DB error: {exc}")
        return {"success": False, "error": str(exc)}


def save_session_key(session_key: str, profile_id: str):
    """Save nurse session key — profile_id must already exist in profiles table"""
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
                .select("profile_id, expires_at, used") \
                .eq("access_code", session_key) \
                .eq("used", False) \
                .execute()
            if not result.data:
                return {"success": False, "error": "Invalid or expired session key"}
            row = result.data[0]
            expires_at = _parse_datetime(row["expires_at"])
            if expires_at < datetime.now(timezone.utc):
                return {"success": False, "error": "Session key expired"}
            return {"success": True, "patient_id": row["profile_id"]}

        with _local_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT profile_id, expires_at FROM nurse_sessions WHERE access_code = %s AND used = false ORDER BY created_at DESC LIMIT 1",
                    (session_key,),
                )
                row = cursor.fetchone()
                if not row:
                    return {"success": False, "error": "Invalid or expired session key"}
                expires_at = _parse_datetime(row["expires_at"])
                if expires_at < datetime.now(timezone.utc):
                    return {"success": False, "error": "Session key expired"}
                cursor.execute("UPDATE nurse_sessions SET used = true WHERE access_code = %s", (session_key,))
            connection.commit()
        return {"success": True, "patient_id": str(row["profile_id"])}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


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
        daily = sum(1 for profile in profiles if str(profile.get("created_at", ""))[:10] == today)
        risk_flags = sum(
            1
            for profile in profiles
            if (profile.get("smoking") and (profile.get("age") or 0) > 35)
            or profile.get("migraine_type") == "with_aura"
        )

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
            age = profile.get("age") or 0
            is_high = (profile.get("smoking") and age > 35) or profile.get("migraine_type") == "with_aura"
            is_medium = profile.get("smoking") or profile.get("migraine_type") == "without_aura"
            recent.append({
                "id": str(profile["profile_id"])[:8].upper(),
                "age": age,
                "status": "Flagged" if is_high else "Active",
                "riskLevel": "High" if is_high else ("Medium" if is_medium else "Low"),
                "recommendation": "Copper IUD" if not profile.get("breastfeeding") else "Progestin-only Pill",
                "lastVisit": str(profile.get("created_at", ""))[:10],
            })

        return {"success": True, "data": {
            "activeConsultations": total,
            "riskFlags": risk_flags,
            "dailySessions": daily,
            "recentPatients": recent,
            "ageDemographics": [{"range": key, "count": value} for key, value in buckets.items()],
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
