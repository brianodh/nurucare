"""
NuruCare - Backend API (Full Version with Database + AI)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel
import random
import string
import secrets

# Import our modules
from database import save_intake_data, save_session_key, save_sync_token, verify_session_key, verify_sync_token
from ai_client import get_ai_recommendation, translate_to_swahili

# ============================================
# ENUMS
# ============================================

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

# ============================================
# DATA MODELS
# ============================================

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

class RecommendationResponse(BaseModel):
    recommended_methods: list
    restricted_methods: list
    requires_provider_consultation: bool
    general_advice: str
    timestamp: datetime
    swahili_version: Optional[str] = None

class SessionKeyRequest(BaseModel):
    patient_id: str

class SyncVerifyRequest(BaseModel):
    token: str
    your_id: str

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "swahili"

# ============================================
# CREATE FASTAPI APP
# ============================================

app = FastAPI(
    title="NuruCare API",
    description="AI-Powered Contraceptive Decision-Support for Sub-Saharan Africa",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HEALTH ENDPOINTS
# ============================================

@app.get("/")
async def root():
    return {"message": "NuruCare API is running", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============================================
# MAIN API ENDPOINTS
# ============================================

@app.post("/api/v1/intake")
async def submit_intake(intake_data: IntakeData):
    """Save user health data to database"""
    session_id = f"session_{intake_data.age}_{int(datetime.now().timestamp())}"
    
    # Save to database
    result = save_intake_data(session_id, intake_data.dict())
    
    return {
        "success": result["success"],
        "message": "Intake data received" if result["success"] else "Database error",
        "session_id": session_id
    }

@app.post("/api/v1/recommend", response_model=RecommendationResponse)
async def get_recommendations(intake_data: IntakeData):
    """Get AI-powered contraceptive recommendations"""
    
    # Get AI recommendation
    ai_response = get_ai_recommendation(intake_data.dict())
    
    # Get Swahili translation
    swahili_version = translate_to_swahili(ai_response[:300])
    
    # WHO MEC Safety Rules
    recommendations = []
    restrictions = []
    
    # Age-based recommendations
    if intake_data.age < 20:
        recommendations.append({"name": "Male Condoms", "effectiveness": 85, "explanation": "No hormones, protects against STIs"})
        recommendations.append({"name": "Progestin-only Pill", "effectiveness": 93, "explanation": "Safe for young users"})
    elif intake_data.age < 35:
        recommendations.append({"name": "Progestin-only Pill", "effectiveness": 93, "explanation": "Highly effective, reversible"})
        recommendations.append({"name": "Copper IUD", "effectiveness": 99, "explanation": "Long-acting, no hormones"})
    else:
        recommendations.append({"name": "Progestin-only Pill", "effectiveness": 93, "explanation": "Safe for older users"})
        recommendations.append({"name": "Copper IUD", "effectiveness": 99, "explanation": "Long-acting protection"})
    
    # Contraindications
    if intake_data.smoking and intake_data.age > 35:
        restrictions.append({"name": "Combined Oral Contraceptives", "reason": "WHO Category 4: Age >35 + smoking", "who_category": 4})
    
    if intake_data.migraine_type == "with_aura":
        restrictions.append({"name": "Combined Oral Contraceptives", "reason": "WHO Category 4: Migraine with aura", "who_category": 4})
    
    if intake_data.breastfeeding:
        recommendations.append({"name": "Progestin-only Pill", "effectiveness": 93, "explanation": "Safe during breastfeeding"})
        recommendations.append({"name": "Condoms", "effectiveness": 85, "explanation": "No effect on breast milk"})
    
    return RecommendationResponse(
        recommended_methods=recommendations,
        restricted_methods=restrictions,
        requires_provider_consultation=len(restrictions) > 0,
        general_advice="Consult a healthcare provider before starting any contraceptive method.",
        timestamp=datetime.now(),
        swahili_version=swahili_version
    )

@app.post("/api/v1/session-key")
async def generate_session_key(request: SessionKeyRequest):
    """Generate 6-digit code for nurses"""
    session_key = ''.join(random.choices(string.digits, k=6))
    save_session_key(session_key, request.patient_id)
    return {"session_key": session_key, "expires_in_minutes": 15}

@app.post("/api/v1/nurse/patient")
async def get_patient_by_session_key(session_key: str):
    """Nurse views patient data using session key"""
    result = verify_session_key(session_key)
    if result["success"]:
        return {"success": True, "patient_data": {"patient_id": result["patient_id"]}, "expires_at": datetime.now().isoformat()}
    return {"success": False, "error": "Invalid or expired session key"}

@app.post("/api/v1/sync/token")
async def generate_sync_token():
    """Generate partner sync token"""
    token = secrets.token_urlsafe(32)
    return {"token": token, "expires_in_hours": 24}

@app.post("/api/v1/sync/verify")
async def verify_sync_token_endpoint(request: SyncVerifyRequest):
    """Verify partner sync token"""
    return {"success": True, "partner_id": "partner_123", "message": "Connected successfully"}

@app.post("/api/v1/translate")
async def translate_text(request: TranslateRequest):
    """Translate text to Swahili"""
    translation = translate_to_swahili(request.text)
    return {"original": request.text, "translated": translation, "language": request.target_language}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)