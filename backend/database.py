"""
NuruCare - Database Connection (Mock Mode - No API Keys Required)
This version works without Supabase. Add real keys later.
"""

from datetime import datetime
import uuid

# Mock database storage (in-memory, works immediately)
_mock_intake_data = {}
_mock_session_keys = {}
_mock_sync_tokens = {}

def save_intake_data(session_id: str, intake_data: dict):
    """Save user intake data - mock version that always works"""
    _mock_intake_data[session_id] = {
        "data": intake_data,
        "created_at": datetime.now().isoformat()
    }
    print(f"✅ Mock: Saved intake data for session {session_id}")
    return {"success": True, "message": "Data saved successfully"}

def save_session_key(session_key: str, patient_id: str):
    """Save nurse session key - mock version"""
    _mock_session_keys[session_key] = {
        "patient_id": patient_id,
        "expires_at": datetime.now().replace(microsecond=0).isoformat()
    }
    print(f"✅ Mock: Saved session key {session_key} for patient {patient_id}")
    return {"success": True}

def save_sync_token(token: str, from_user_id: str):
    """Save partner sync token - mock version"""
    _mock_sync_tokens[token] = {
        "from_user_id": from_user_id,
        "expires_at": datetime.now().replace(microsecond=0).isoformat()
    }
    print(f"✅ Mock: Saved sync token for user {from_user_id}")
    return {"success": True}

def verify_session_key(session_key: str):
    """Verify if session key is valid - mock version"""
    if session_key in _mock_session_keys:
        key_data = _mock_session_keys[session_key]
        expires_at = datetime.fromisoformat(key_data["expires_at"])
        if expires_at > datetime.now():
            return {"success": True, "patient_id": key_data["patient_id"]}
    return {"success": False, "error": "Invalid or expired session key"}

def verify_sync_token(token: str):
    """Verify if sync token is valid - mock version"""
    if token in _mock_sync_tokens:
        token_data = _mock_sync_tokens[token]
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if expires_at > datetime.now():
            return {"success": True, "from_user_id": token_data["from_user_id"]}
    return {"success": False, "error": "Invalid or expired token"}

def get_supabase():
    """Return None since we're in mock mode"""
    return None

print("✅ Database running in MOCK MODE (no API keys needed)")