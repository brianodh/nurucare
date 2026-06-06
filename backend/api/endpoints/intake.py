from datetime import datetime

from fastapi import APIRouter, HTTPException

from backend.crypto import generate_nurse_session_key, generate_partner_sync_token, validate_nurse_session_key
from backend.engine.guardrail import WHOMECGuardrail
from backend.api.schemas.profile import (
    IntakeProfile,
    IntakeResponse,
    NurseKeyResponse,
    NurseKeyVerifyRequest,
    PartnerSyncResponse,
)

router = APIRouter()
guardrail = WHOMECGuardrail()


@router.post("/intake", response_model=IntakeResponse)
def intake_profile(profile: IntakeProfile):
    user_profile = profile.model_dump()
    evaluation = guardrail.evaluate(user_profile)

    if evaluation["requires_provider"]:
        recommended = []
    else:
        recommended = evaluation["allowed_methods"][:4]

    confidence_score = max(30, 100 - len(evaluation["restricted_methods"]) * 12)
    return IntakeResponse(
        recommended_methods=recommended,
        restricted_methods=evaluation["restricted_methods"],
        explanations=evaluation["explanations"],
        confidence_score=confidence_score,
        requires_provider=evaluation["requires_provider"],
    )


@router.post("/partner-sync", response_model=PartnerSyncResponse)
def create_partner_sync():
    token, minutes = generate_partner_sync_token()
    return PartnerSyncResponse(sync_token=token, expires_in_minutes=minutes)


@router.post("/nurse-session", response_model=NurseKeyResponse)
def create_nurse_session():
    code, minutes = generate_nurse_session_key()
    return NurseKeyResponse(access_code=code, expires_in_minutes=minutes)


@router.post("/nurse-session/verify")
def verify_nurse_code(payload: NurseKeyVerifyRequest):
    if not validate_nurse_session_key(payload.access_code):
        raise HTTPException(status_code=400, detail="Access code is invalid or expired")
    return {"status": "verified", "verified_at": datetime.utcnow().isoformat()}
