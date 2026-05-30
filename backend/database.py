"""
NuruCare - Supabase Database Connection
Handles all database operations
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# Supabase credentials 
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jklrmoogyprolwftdxnu.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_M7Q1i6l6Zk93ugDlULiY1w_ngdNC3_V")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase():
    """Return Supabase client for API endpoints"""
    return supabase

def save_intake_data(session_id: str, intake_data: dict):
    """Save user intake data to database"""
    try:
        result = supabase.table("user_intake").insert({
            "session_id": session_id,
            "intake_data": intake_data,
            "created_at": datetime.now().isoformat()
        }).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        print(f"Database error: {e}")
        return {"success": False, "error": str(e)}

def save_session_key(session_key: str, patient_id: str):
    """Save nurse session key to database"""
    try:
        result = supabase.table("nurse_session_keys").insert({
            "session_key": session_key,
            "patient_id": patient_id,
            "expires_at": datetime.now().replace(microsecond=0).isoformat(),
            "created_at": datetime.now().isoformat()
        }).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        print(f"Database error: {e}")
        return {"success": False, "error": str(e)}

def save_sync_token(token: str, from_user_id: str):
    """Save partner sync token to database"""
    try:
        result = supabase.table("sync_tokens").insert({
            "token": token,
            "from_user_id": from_user_id,
            "expires_at": datetime.now().replace(microsecond=0).isoformat(),
            "created_at": datetime.now().isoformat()
        }).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        print(f"Database error: {e}")
        return {"success": False, "error": str(e)}

def verify_session_key(session_key: str):
    """Verify if session key is valid and not expired"""
    try:
        result = supabase.table("nurse_session_keys").select("*").eq("session_key", session_key).execute()
        if result.data:
            key_data = result.data[0]
            expires_at = datetime.fromisoformat(key_data["expires_at"])
            if expires_at > datetime.now():
                return {"success": True, "patient_id": key_data["patient_id"]}
        return {"success": False, "error": "Invalid or expired session key"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_sync_token(token: str):
    """Verify if sync token is valid and not expired"""
    try:
        result = supabase.table("sync_tokens").select("*").eq("token", token).execute()
        if result.data:
            token_data = result.data[0]
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if expires_at > datetime.now():
                return {"success": True, "from_user_id": token_data["from_user_id"]}
        return {"success": False, "error": "Invalid or expired token"}
    except Exception as e:
        return {"success": False, "error": str(e)}