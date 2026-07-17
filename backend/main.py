"""
NuruCare - Backend API
"""

import secrets
import string
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import (
    save_intake_data, save_session_key, save_sync_token,
    verify_session_key, verify_sync_token, get_profile_by_id,
    get_dashboard_data,
)
from ai_client import get_ai_recommendation, translate_to_swahili
from auth import (
    NurseLoginRequest, TokenResponse, PatientSessionResponse,
    create_access_token, verify_password, NURSE_ACCOUNTS,
    require_nurse, require_patient, optional_auth, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# ── Token Generation Helper ──────────────────────────────────
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # Removed confusing chars 0,O,1,I,l,5,S

def generate_user_friendly_token(prefix="NX"):
    """Generate a human-readable token like NX-7K9-2M4"""
    random_bytes = secrets.token_bytes(8)
    num = int.from_bytes(random_bytes, byteorder='big')
    parts = []
    for _ in range(2):
        part = []
        for _ in range(3):
            num, char_index = divmod(num, len(ALPHABET))
            part.append(ALPHABET[char_index])
        parts.append(''.join(part))
    return f"{prefix}-{parts[0]}-{parts[1]}"

# ── Enums ─────────────────────────────────────────────────
class Gender(str, Enum):
    female = "female"
    male = "male"

class MigraineType(str, Enum):
    none = "none"
    without_aura = "without_aura"
    with_aura = "with_aura"

class FertilityIntention(str, Enum):
    short_term = "short_term"
    long_term = "long_term"
    no_more = "no_more"
    unsure = "unsure"

# ── Request / Response models ─────────────────────────────
class IntakeData(BaseModel):
    age: int
    gender: Gender
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    smoking: bool = False
    migraine_type: MigraineType = MigraineType.none
    is_pregnant: bool = False
    breastfeeding: bool = False
    fertility_intention: FertilityIntention
    parity: int = 0

class SyncGenerateRequest(BaseModel):
    profile_id: Optional[str] = None  # optional — will auto-create if not provided

class SyncVerifyRequest(BaseModel):
    token: str
    profile_id: Optional[str] = None

class SessionKeyRequest(BaseModel):
    profile_id: Optional[str] = None  # optional — will auto-create if not provided

class NurseVerifySessionRequest(BaseModel):
    session_key: str

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "swahili"

# ── App ───────────────────────────────────────────────────
app = FastAPI(
    title="NuruCare API",
    description="AI-Powered Contraceptive Decision-Support for Sub-Saharan Africa",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "NuruCare API is running", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.post("/api/v1/auth/nurse/login", response_model=TokenResponse)
async def nurse_login(request: NurseLoginRequest):
    """Nurse login with username + password → JWT"""
    account = NURSE_ACCOUNTS.get(request.username)
    if not account or not verify_password(request.password, account["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": request.username, "role": "nurse", "name": account["name"]})
    return TokenResponse(
        access_token=token,
        role="nurse",
        name=account["name"],
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@app.post("/api/v1/auth/patient/session", response_model=PatientSessionResponse)
async def create_patient_session():
    """
    Create an anonymous patient session.
    Saves a minimal profile row → returns profile_id + JWT.
    No name, email, or phone stored — privacy by design.
    """
    result = save_intake_data(None, {
        "age": 0, "systolic_bp": 0, "diastolic_bp": 0,
        "smoking": False, "migraine_type": "none", "breastfeeding": False,
    })
    if not result["success"]:
        raise HTTPException(status_code=500, detail="Failed to create session")

    profile_id = result["profile_id"]
    token = create_access_token({"sub": profile_id, "role": "patient"}, expires_minutes=60 * 24)
    return PatientSessionResponse(profile_id=profile_id, access_token=token)

@app.get("/api/v1/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Return current authenticated user info"""
    return {"sub": user.get("sub"), "role": user.get("role"), "name": user.get("name")}

# ═══════════════════════════════════════════════════════════
# INTAKE & RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════

@app.post("/api/v1/intake")
async def submit_intake(intake_data: IntakeData, user: Optional[dict] = Depends(optional_auth)):
    """Save full intake data — updates the profile if patient is authenticated"""
    profile_id = user.get("sub") if user and user.get("role") == "patient" else None
    result = save_intake_data(profile_id, intake_data.dict())
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to save intake"))
    return {"success": True, "message": "Intake data received", "profile_id": result["profile_id"]}


@app.get("/api/v1/patient/profile")
async def get_patient_profile(user: dict = Depends(get_current_user)):
    """Get current patient's profile"""
    if user.get("role") != "patient":
        raise HTTPException(status_code=403, detail="Patient access required")
    profile_id = user.get("sub")
    result = get_profile_by_id(profile_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"success": True, "profile": result["data"]}

@app.post("/api/v1/recommend")
async def get_recommendations(intake_data: IntakeData):
    """Get contraceptive recommendations — WHO MEC rules run instantly, AI runs async"""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    recommendations = []
    restrictions = []

    # ─ WHO MEC rules (instant, no API call) ────────────────────
    if intake_data.age < 20:
        recommendations.append({"name": "Male Condoms", "effectiveness": 85, "explanation": "No hormones, protects against STIs"})
        recommendations.append({"name": "Progestin-only Pill", "effectiveness": 93, "explanation": "Safe for young users"})
    elif intake_data.age < 35:
        recommendations.append({"name": "Progestin-only Pill", "effectiveness": 93, "explanation": "Highly effective, reversible"})
        recommendations.append({"name": "Copper IUD", "effectiveness": 99, "explanation": "Long-acting, no hormones"})
    else:
        recommendations.append({"name": "Progestin-only Pill", "effectiveness": 93, "explanation": "Safe for older users"})
        recommendations.append({"name": "Copper IUD", "effectiveness": 99, "explanation": "Long-acting protection"})

    recommendations.append({"name": "Male Condoms", "effectiveness": 85, "explanation": "Protects against STIs"})

    if intake_data.smoking and intake_data.age > 35:
        restrictions.append({"name": "Combined Oral Contraceptives", "reason": "WHO Category 4: Age >35 + smoking increases cardiovascular risk", "who_category": 4})
    if intake_data.migraine_type == "with_aura":
        restrictions.append({"name": "Combined Oral Contraceptives", "reason": "WHO Category 4: Migraine with aura increases stroke risk", "who_category": 4})
    if intake_data.breastfeeding:
        recommendations.append({"name": "Progestin-only Pill (POP)", "effectiveness": 93, "explanation": "Safe during breastfeeding"})
        recommendations.append({"name": "Lactational Amenorrhea Method (LAM)", "effectiveness": 98, "explanation": "For exclusively breastfeeding mothers <6 months"})

    # ─ AI narrative (run in thread so it doesn’t block) ─────────
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        ai_response, swahili_version = await asyncio.gather(
            loop.run_in_executor(pool, get_ai_recommendation, intake_data.dict()),
            loop.run_in_executor(pool, translate_to_swahili, recommendations[0]["explanation"] if recommendations else "")
        )

    return {
        "recommended_methods": recommendations,
        "restricted_methods": restrictions,
        "requires_provider_consultation": len(restrictions) > 0,
        "general_advice": "Always consult a healthcare provider before starting any contraceptive method.",
        "timestamp": datetime.now().isoformat(),
        "swahili_version": swahili_version,
        "full_ai_response": ai_response,
    }

# ═══════════════════════════════════════════════════════════
# NURSE SESSION KEYS
# ═══════════════════════════════════════════════════════════

@app.post("/api/v1/session-key")
async def generate_session_key(request: SessionKeyRequest, user: Optional[dict] = Depends(optional_auth)):
    """Patient generates a 6-digit code to share with nurse. Auto-creates a profile if none provided."""
    profile_id = request.profile_id
    if not profile_id and user and user.get("role") == "patient":
        profile_id = user.get("sub")

    # Auto-create anonymous profile if not provided
    if not profile_id:
        created = save_intake_data(None, {
            "age": 0, "systolic_bp": 0, "diastolic_bp": 0,
            "smoking": False, "migraine_type": "none", "breastfeeding": False,
        })
        if not created["success"]:
            raise HTTPException(status_code=500, detail="Failed to create anonymous profile")
        profile_id = created["profile_id"]

    session_key = ''.join(secrets.choice(string.digits) for _ in range(6))
    result = save_session_key(session_key, profile_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate session key"))

    return {"session_key": session_key, "profile_id": profile_id, "expires_in_minutes": 15}

@app.post("/api/v1/nurse/verify-session")
async def nurse_verify_session(request: NurseVerifySessionRequest):
    """Nurse enters 6-digit code → gets patient profile."""
    result = verify_session_key(request.session_key)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Invalid or expired session key"))

    profile = get_profile_by_id(result["patient_id"])
    if not profile["success"]:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    return {"success": True, "patient_data": profile["data"]}

# ═══════════════════════════════════════════════════════════
# PARTNER SYNC
# ═══════════════════════════════════════════════════════════

@app.post("/api/v1/sync/token")
async def generate_sync_token(request: SyncGenerateRequest, user: Optional[dict] = Depends(optional_auth)):
    """Generate anonymous partner sync token. Auto-creates a profile if none provided."""
    profile_id = request.profile_id
    if not profile_id and user and user.get("role") == "patient":
        profile_id = user.get("sub")

    # Auto-create anonymous profile if not provided
    if not profile_id:
        created = save_intake_data(None, {
            "age": 0, "systolic_bp": 0, "diastolic_bp": 0,
            "smoking": False, "migraine_type": "none", "breastfeeding": False,
        })
        if not created["success"]:
            raise HTTPException(status_code=500, detail="Failed to create anonymous profile")
        profile_id = created["profile_id"]

    token = generate_user_friendly_token()
    result = save_sync_token(token, profile_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate sync token"))

    return {"token": token, "profile_id": profile_id, "expires_in_hours": 24}

@app.post("/api/v1/sync/verify")
async def verify_sync_token_endpoint(request: SyncVerifyRequest):
    """Partner enters the sync token → profiles are linked, partner profile returned"""
    result = verify_sync_token(request.token)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Invalid or expired token"))

    linked_profile_id = result["from_user_id"]
    partner_profile = None
    if linked_profile_id:
        profile = get_profile_by_id(linked_profile_id)
        if profile["success"]:
            partner_profile = profile["data"]

    return {
        "success": True,
        "linked_profile_id": linked_profile_id,
        "partner_profile": partner_profile,
        "message": "Partner connected successfully",
    }

# ═══════════════════════════════════════════════════════════
# NURSE DASHBOARD (protected)
# ═══════════════════════════════════════════════════════════

@app.get("/api/v1/nurse/dashboard")
async def get_dashboard(nurse: dict = Depends(require_nurse)):
    """Fetch dashboard stats — nurse JWT required"""
    result = get_dashboard_data()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result["data"]

# ═══════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════

@app.post("/api/v1/translate")
async def translate_text(request: TranslateRequest):
    translation = translate_to_swahili(request.text)
    return {"original": request.text, "translated": translation, "language": request.target_language}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
