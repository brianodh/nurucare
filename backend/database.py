"""
NuruCare - Database Connection (Supabase)
"""

import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

def get_supabase() -> Client:
    return _supabase

def save_intake_data(session_id: str, intake_data: dict):
    try:
        row = {
            "age": intake_data["age"],
            "systolic_bp": intake_data.get("systolic_bp") or 0,
            "diastolic_bp": intake_data.get("diastolic_bp") or 0,
            "smoking": intake_data.get("smoking", False),
            "migraine_type": intake_data.get("migraine_type", "none"),
            "breastfeeding": intake_data.get("breastfeeding", False),
        }
        result = _supabase.table("profiles").insert(row).execute()
        profile_id = result.data[0]["profile_id"]
        print(f"✅ Supabase: Saved intake for profile {profile_id}")
        return {"success": True, "profile_id": profile_id}
    except Exception as e:
        print(f"❌ Supabase error: {e}")
        return {"success": False, "error": str(e)}

def save_session_key(session_key: str, profile_id: str):
    """Save nurse session key — profile_id must already exist in profiles table"""
    try:
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        _supabase.table("nurse_sessions").insert({
            "profile_id": profile_id,
            "access_code": session_key,
            "expires_at": expires_at,
        }).execute()
        return {"success": True}
    except Exception as e:
        print(f"❌ Supabase error (session key): {e}")
        return {"success": False, "error": str(e)}

def save_sync_token(token: str, from_profile_id: str):
    """Save partner sync token linked to a real profile_id"""
    try:
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        row = {
            "sync_token_hash": token,
            "expires_at": expires_at,
            "profile_id": from_profile_id,
        }
        _supabase.table("partner_sync").insert(row).execute()
        return {"success": True}
    except Exception as e:
        print(f"❌ Supabase error (sync token): {e}")
        return {"success": False, "error": str(e)}

def verify_session_key(session_key: str):
    try:
        result = _supabase.table("nurse_sessions")\
            .select("profile_id, expires_at, used")\
            .eq("access_code", session_key)\
            .eq("used", False)\
            .execute()
        if not result.data:
            return {"success": False, "error": "Invalid or expired session key"}
        row = result.data[0]
        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            return {"success": False, "error": "Session key expired"}
        return {"success": True, "patient_id": row["profile_id"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_dashboard_data():
    try:
        profiles = _supabase.table("profiles").select("*").order("created_at", desc=True).execute().data
        total = len(profiles)

        # Stat counts
        today = datetime.now(timezone.utc).date().isoformat()
        daily = sum(1 for p in profiles if p.get("created_at", "")[:10] == today)
        risk_flags = sum(1 for p in profiles if p.get("smoking") and (p.get("age") or 0) > 35
                         or p.get("migraine_type") == "with_aura")

        # Age demographics
        buckets = {"15-19": 0, "20-24": 0, "25-29": 0, "30-34": 0, "35-39": 0, "40+": 0}
        for p in profiles:
            age = p.get("age") or 0
            if age < 20: buckets["15-19"] += 1
            elif age < 25: buckets["20-24"] += 1
            elif age < 30: buckets["25-29"] += 1
            elif age < 35: buckets["30-34"] += 1
            elif age < 40: buckets["35-39"] += 1
            else: buckets["40+"] += 1

        # Recent patients table (last 10)
        recent = []
        for p in profiles[:10]:
            age = p.get("age") or 0
            is_high = (p.get("smoking") and age > 35) or p.get("migraine_type") == "with_aura"
            is_medium = p.get("smoking") or p.get("migraine_type") == "without_aura"
            risk = "High" if is_high else ("Medium" if is_medium else "Low")
            recent.append({
                "id": p["profile_id"][:8].upper(),
                "age": age,
                "status": "Flagged" if is_high else "Active",
                "riskLevel": risk,
                "recommendation": "Copper IUD" if not p.get("breastfeeding") else "Progestin-only Pill",
                "lastVisit": p.get("created_at", "")[:10],
            })

        return {"success": True, "data": {
            "activeConsultations": total,
            "riskFlags": risk_flags,
            "dailySessions": daily,
            "recentPatients": recent,
            "ageDemographics": [{"range": k, "count": v} for k, v in buckets.items()],
        }}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_profile_by_id(profile_id: str):
    try:
        result = _supabase.table("profiles").select("*").eq("profile_id", profile_id).execute()
        if not result.data:
            return {"success": False, "error": "Profile not found"}
        return {"success": True, "data": result.data[0]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_sync_token(token: str):
    try:
        result = _supabase.table("partner_sync")\
            .select("profile_id, expires_at")\
            .eq("sync_token_hash", token)\
            .execute()
        if not result.data:
            return {"success": False, "error": "Invalid token"}
        row = result.data[0]
        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            return {"success": False, "error": "Token expired"}
        return {"success": True, "from_user_id": row["profile_id"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

print("✅ Database connected to Supabase")
