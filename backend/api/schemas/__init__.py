"""
NuruCare - Pydantic Schemas (Data Validation Models)
======================================================

This file defines the data structures for API requests and responses.
Pydantic automatically validates data types and required fields.

Author: Alois Karanja Gitau
Date: May 27, 2026
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =========================================================
# ENUMS (Predefined choices for dropdowns)
# =========================================================

class Gender(str, Enum):
    """User gender options"""
    FEMALE = "female"
    MALE = "male"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class MigraineType(str, Enum):
    """Migraine classification for WHO MEC rules"""
    NONE = "none"
    WITHOUT_AURA = "without_aura"
    WITH_AURA = "with_aura"

class FertilityIntention(str, Enum):
    """User's pregnancy intentions"""
    WANT_SOON = "want_soon"        # Within 1 year
    WANT_LATER = "want_later"      # 1-5 years
    NO_MORE = "no_more"             # No more children
    UNSURE = "unsure"               # Undecided

class CycleRegularity(str, Enum):
    """Menstrual cycle regularity"""
    REGULAR = "regular"
    IRREGULAR = "irregular"
    NOT_APPLICABLE = "not_applicable"

class EducationLevel(str, Enum):
    """Education level for literacy-appropriate responses"""
    NONE = "none"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"

class FPStatus(str, Enum):
    """Family planning user status"""
    NEW = "new"
    RETURNING = "returning"
    NON_USER = "non_user"


# =========================================================
# REQUEST SCHEMAS (What frontend sends to backend)
# =========================================================

class IntakeRequest(BaseModel):
    """
    Validates the user's health intake form data.
    Used when user submits the 8-question intake form.
    """
    
    # Demographics
    age: int = Field(..., ge=15, le=60, description="Age in years (15-60)")
    gender: Gender = Field(..., description="User's gender")
    education: Optional[EducationLevel] = Field(None, description="Education level")
    
    # Clinical data for WHO MEC rules
    smoking: bool = Field(False, description="Current smoker")
    migraine_type: MigraineType = Field(MigraineType.NONE, description="Migraine type")
    systolic_bp: int = Field(..., ge=60, le=250, description="Systolic blood pressure (mmHg)")
    diastolic_bp: int = Field(..., ge=40, le=150, description="Diastolic blood pressure (mmHg)")
    
    # Reproductive health
    cycle_regularity: Optional[CycleRegularity] = Field(None, description="Menstrual cycle regularity")
    cycle_length_days: Optional[int] = Field(None, ge=20, le=40, description="Average cycle length in days")
    
    # Fertility intentions
    fertility_intention: FertilityIntention = Field(..., description="Pregnancy intentions")
    parity: int = Field(0, ge=0, le=15, description="Number of children")
    
    # Special conditions
    breastfeeding: bool = Field(False, description="Currently breastfeeding")
    postpartum_weeks: Optional[int] = Field(None, ge=0, le=52, description="Weeks since delivery")
    
    # Side effect concerns
    side_effect_concerns: List[str] = Field(default_factory=list, description="Concerns like weight_gain, mood_changes")
    
    @validator('postpartum_weeks')
    def validate_postpartum(cls, v, values):
        """Ensure postpartum_weeks is provided if breastfeeding is True"""
        if values.get('breastfeeding') and v is None:
            raise ValueError('postpartum_weeks is required when breastfeeding is True')
        return v
    
    @validator('cycle_length_days')
    def validate_cycle_length(cls, v, values):
        """Ensure cycle length is provided if cycle_regularity is specified"""
        if values.get('cycle_regularity') and values.get('cycle_regularity') != CycleRegularity.NOT_APPLICABLE:
            if v is None:
                raise ValueError('cycle_length_days is required when cycle_regularity is specified')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 28,
                "gender": "female",
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 118,
                "diastolic_bp": 78,
                "cycle_regularity": "regular",
                "cycle_length_days": 28,
                "fertility_intention": "want_later",
                "parity": 1,
                "breastfeeding": False,
                "side_effect_concerns": ["weight_gain"]
            }
        }


class SessionKeyRequest(BaseModel):
    """
    Validates the 6-digit session key for nurse/doctor access.
    """
    session_key: str = Field(..., min_length=6, max_length=6, description="6-digit session key")
    
    @validator('session_key')
    def validate_session_key(cls, v):
        """Ensure session key is exactly 6 digits"""
        if not v.isdigit():
            raise ValueError('Session key must contain only digits')
        return v
    
    class Config:
        json_schema_extra = {"example": {"session_key": "123456"}}


class SyncTokenRequest(BaseModel):
    """
    Validates the partner sync token.
    """
    token: str = Field(..., min_length=8, max_length=64, description="Partner sync token")
    
    class Config:
        json_schema_extra = {"example": {"token": "a7f3e9c2"}}


# =========================================================
# RESPONSE SCHEMAS (What backend sends to frontend)
# =========================================================

class RestrictedMethod(BaseModel):
    """
    Information about a restricted contraceptive method.
    """
    method_id: str
    method_name: str
    category: int = Field(..., ge=1, le=4, description="WHO MEC category (1-4)")
    explanation: str
    rule_id: str


class RecommendedMethod(BaseModel):
    """
    Information about a recommended contraceptive method.
    """
    method_id: str
    method_name: str
    confidence_score: float = Field(..., ge=0, le=100, description="Match score (0-100%)")
    explanation: str
    benefits: List[str] = Field(default_factory=list)
    side_effects: List[str] = Field(default_factory=list)
    myth_buster: Optional[str] = None


class RecommendationResponse(BaseModel):
    """
    Complete recommendation response from the AI engine.
    """
    # Recommendations
    recommended_methods: List[RecommendedMethod] = Field(..., description="Top recommended methods")
    
    # Safety
    restricted_methods: Dict[str, List[RestrictedMethod]] = Field(default_factory=dict, description="Methods that are unsafe")
    
    # Clinical guidance
    requires_provider: bool = Field(False, description="User needs to consult a healthcare provider")
    
    # Education
    myth_busters: List[str] = Field(default_factory=list, description="Myth-busting facts")
    
    # Metadata
    disclaimer: str = Field("This is not medical advice. Consult a healthcare provider before starting any contraceptive method.")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommended_methods": [
                    {
                        "method_id": "implants",
                        "method_name": "Implant (Jadelle)",
                        "confidence_score": 92,
                        "explanation": "The implant is 99% effective and lasts 5 years.",
                        "benefits": ["Long-lasting", "Very effective", "Reversible"],
                        "side_effects": ["Irregular bleeding first 3-6 months"],
                        "myth_buster": "Implants do NOT cause infertility."
                    }
                ],
                "restricted_methods": {},
                "requires_provider": False,
                "myth_busters": ["Implants do not cause infertility. Fertility returns immediately after removal."],
                "disclaimer": "This is not medical advice...",
                "timestamp": "2026-05-27T10:30:00"
            }
        }


class GuardrailResponse(BaseModel):
    """
    Simplified guardrail evaluation response (for internal use).
    """
    restricted_methods: Dict[str, List[Dict[str, Any]]]
    allowed_methods: List[str]
    explanations: List[Dict[str, str]]
    requires_provider: bool
    summary: str
    rule_count: int


class HealthProfileResponse(BaseModel):
    """
    User health profile (masked for privacy) - for nurse dashboard.
    """
    profile_id: str
    age: int
    gender: str
    fertility_intention: str
    parity: int
    has_hypertension: bool
    requires_provider: bool
    created_at: str
    expires_at: str  # Session expiration


class SyncTokenResponse(BaseModel):
    """
    Response when generating a partner sync token.
    """
    token: str
    expires_in_minutes: int = Field(15, description="Token expires in 15 minutes")
    message: str = "Share this token with your partner to sync contraception decisions."


class SessionKeyResponse(BaseModel):
    """
    Response when generating a nurse session key.
    """
    session_key: str
    expires_in_minutes: int = Field(15, description="Key expires in 15 minutes")
    message: str = "Share this 6-digit code with the nurse for secure access."


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    """
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "age must be between 15 and 60",
                "timestamp": "2026-05-27T10:30:00"
            }
        }


class HealthCheckResponse(BaseModel):
    """
    API health check response.
    """
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    services: Dict[str, bool] = {
        "guardrail_engine": True,
        "database": True
    }


# =========================================================
# INTERNAL SCHEMAS (For backend processing)
# =========================================================

class GuardrailInput(BaseModel):
    """
    Internal schema for guardrail engine input.
    Matches what WHOMECGuardrail.evaluate() expects.
    """
    age: int
    smoking: bool
    migraine_type: str
    systolic_bp: int
    diastolic_bp: int
    breastfeeding: bool
    postpartum_weeks: int = 100  # Default to not recently postpartum


class UserProfileDB(BaseModel):
    """
    Database schema for storing user profiles (PostgreSQL).
    """
    profile_id: str
    session_key_hash: str  # Hashed for security
    encrypted_data: str    # Encrypted health data
    created_at: datetime
    expires_at: datetime
    accessed_at: Optional[datetime] = None