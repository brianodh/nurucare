from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

MigraineType = Literal["none", "without_aura", "with_aura"]
DurationPref = Literal["short_term", "long_term"]


class IntakeProfile(BaseModel):
    age: int = Field(..., ge=10, le=65)
    systolic_bp: int = Field(..., ge=70, le=220)
    diastolic_bp: int = Field(..., ge=40, le=140)
    smoking: bool = False
    migraine_type: MigraineType = "none"
    breastfeeding: bool = False
    postpartum_weeks: Optional[int] = None
    duration_pref: Optional[DurationPref] = None
    side_effects: Optional[List[str]] = Field(default_factory=list)
    last_period_date: Optional[str] = None


class IntakeResponse(BaseModel):
    recommended_methods: List[str]
    restricted_methods: dict
    explanations: List[dict]
    confidence_score: int
    requires_provider: bool


class PartnerSyncResponse(BaseModel):
    sync_token: str
    expires_in_minutes: int


class NurseKeyResponse(BaseModel):
    access_code: str
    expires_in_minutes: int


class NurseKeyVerifyRequest(BaseModel):
    access_code: str = Field(..., min_length=6, max_length=6)
