"""
NuruCare - Backend API (Full Version - Works without API keys)
Updated to include USSD handler for offline accessibility
"""

# Must be the first statement: defers evaluation of type annotations (PEP 563)
# instead of evaluating them eagerly at function-definition time. Needed
# because _map_intake_to_pipeline() (below) annotates a parameter as
# IntakeData, but that class isn't defined until further down this file —
# without this import, that raises NameError: name 'IntakeData' is not
# defined at module-import time, crashing the whole app before it can
# start. database.py already uses this same import for the same reason.
from __future__ import annotations

import os
import secrets
import string
import sys
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

DEFAULT_SECRET_KEY = "nurucare-dev-secret-change-in-production"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()


def _parse_allowed_origins() -> list:
    raw = os.getenv("ALLOWED_ORIGINS", "")
    if not raw:
        dev_defaults = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ]
        if ENVIRONMENT in ("development", "dev", "local"):
            print(f"[WARN] ALLOWED_ORIGINS not set — using dev defaults: {dev_defaults}")
            return dev_defaults
        print(f"[ERROR] ALLOWED_ORIGINS must be set in non-dev environments")
        return []
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _validate_startup_config() -> None:
    from auth import SECRET_KEY as AUTH_SECRET_KEY

    is_prod = ENVIRONMENT in ("production", "prod")

    if is_prod:
        if not AUTH_SECRET_KEY or AUTH_SECRET_KEY == DEFAULT_SECRET_KEY:
            print(
                "[FATAL] Production environment detected but SECRET_KEY is unset or still set"
                f" to the well-known default '{DEFAULT_SECRET_KEY}'. Refusing to boot."
                " Generate a strong secret (e.g., openssl rand -hex 32) and set it"
                " via the SECRET_KEY environment variable."
            )
            sys.exit(1)

    origins = _parse_allowed_origins()
    if is_prod and not origins:
        print(
            "[FATAL] Production environment requires ALLOWED_ORIGINS to be set"
            " (comma-separated list, e.g., https://app.nurucare.org,https://nurucare.org)."
            " Refusing to boot with an empty origin allow-list."
        )
        sys.exit(1)

from database import (
    save_intake_data, save_session_key, save_sync_token,
    verify_session_key, verify_sync_token, get_profile_by_id,
    get_dashboard_data, create_user, get_user_by_username, get_user_by_email,
    update_profile_fields, compute_safety_score,
    rate_limited_verify_session_key, rate_limited_verify_sync_token,
)
from ai_client import get_ai_recommendation, translate_to_swahili
from auth import (
    NurseLoginRequest, TokenResponse, PatientSessionResponse,
    create_access_token, verify_password, hash_password,
    require_nurse, require_patient, require_admin, optional_auth, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from database import get_system_health_detail

# ============================================
# IMPORT USSD & ADMIN ROUTERS
# ============================================
from api.endpoints.ussd import router as ussd_router
from api.endpoints.ussd_complete import router as ussd_complete_router
from api.endpoints.admin import router as admin_router

# ============================================
# RECOMMENDATION ENGINE (lazy loaded)
# ============================================
_RECOMMENDATION_PIPELINE = None


def _get_recommendation_pipeline():
    """Lazy-load the RecommendationPipeline so missing optional deps
    (e.g. pgvector, RAG embeddings table) do not prevent the API from
    booting. The pipeline is the same one used by the USSD flow — it
    runs the full WHO MEC guardrail + ranked recommendations.
    """
    global _RECOMMENDATION_PIPELINE
    if _RECOMMENDATION_PIPELINE is None:
        from engine.recommendation_pipeline import RecommendationPipeline
        _RECOMMENDATION_PIPELINE = RecommendationPipeline()
    return _RECOMMENDATION_PIPELINE


_FERTILITY_INTENT_MAP = {
    "short_term": "want_soon",
    "long_term": "want_later",
    "no_more": "no_more",
    "unsure": "unsure",
}


def _map_intake_to_pipeline(intake_data: IntakeData) -> dict:
    """Map main.py IntakeData fields to RecommendationPipeline input dict."""
    data = intake_data.model_dump()
    data["fertility_intent"] = _FERTILITY_INTENT_MAP.get(
        data.get("fertility_intention", "unsure"), "unsure"
    )
    data.pop("fertility_intention", None)
    data.setdefault("systolic_bp", 0)
    data.setdefault("diastolic_bp", 0)
    data.setdefault("postpartum_weeks", 100)
    return data


def _format_restricted_for_api(restricted) -> list:
    """Flatten pipeline restrictions to the {name, reason, who_category} shape
    historically returned by /api/v1/recommend. Tolerates both a list of dicts
    (pipeline output) and unexpected shapes (e.g. guardrail-native dict form).
    """
    out = []
    seen = set()
    if not restricted:
        return out
    if isinstance(restricted, dict):
        restricted = [
            {"method_id": k, "method_name": str(k).replace("_", " ").title(),
             "category": v if isinstance(v, int) else 3,
             "explanation": "Contraindicated per WHO MEC rules."}
            for k, v in restricted.items()
        ]
    for r in restricted:
        if isinstance(r, str):
            out.append({
                "name": r,
                "reason": "Restricted per WHO MEC rules.",
                "who_category": 3,
            })
            continue
        if not isinstance(r, dict):
            continue
        name = r.get("method_name") or r.get("name")
        if not name:
            continue
        category = r.get("category", r.get("who_category", 3))
        key = (name, category)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "name": name,
            "reason": r.get("explanation") or r.get("reason") or "WHO MEC restriction.",
            "who_category": category,
        })
    return out


def _format_recommended_for_api(recommended) -> list:
    """Flatten pipeline recommendations to {name, effectiveness, explanation}.
    Tolerates non-dict items defensively.
    """
    out = []
    if not recommended:
        return out
    for m in recommended:
        if isinstance(m, str):
            out.append({
                "name": m,
                "effectiveness": 90,
                "explanation": "",
            })
            continue
        if not isinstance(m, dict):
            continue
        name = m.get("method_name") or m.get("name")
        if not name:
            continue
        out.append({
            "name": name,
            "effectiveness": m.get("effectiveness", 90),
            "explanation": m.get("explanation") or "",
            "confidence_score": m.get("confidence_score"),
            "type": m.get("type"),
        })
    return out

# ============================================
# TOKEN GENERATION HELPER
# ============================================
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
# REQUEST / RESPONSE MODELS
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

class SyncGenerateRequest(BaseModel):
    profile_id: Optional[str] = None

class SyncVerifyRequest(BaseModel):
    token: str
    profile_id: Optional[str] = None

class SessionKeyRequest(BaseModel):
    profile_id: Optional[str] = None

class NurseVerifySessionRequest(BaseModel):
    session_key: str

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "swahili"

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "patient"
    gender: Optional[str] = None
    institution_name: Optional[str] = None
    institution_address: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str


_ALLOWED_ORIGINS = _parse_allowed_origins()
_validate_startup_config()

# ============================================
# FASTAPI APP
# ============================================
app = FastAPI(
    title="NuruCare API",
    description="AI-Powered Contraceptive Decision-Support for Sub-Saharan Africa",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print(f"[OK] CORS configured. Allowed origins: {_ALLOWED_ORIGINS}")


# ============================================
# INCLUDE ROUTERS
# ============================================
# Include USSD routers - makes endpoints available at /api/v1/ussd/*
app.include_router(ussd_router, prefix="/api/v1")
app.include_router(ussd_complete_router, prefix="/api/v1")
# Admin endpoints at /api/v1/admin/* — every route internally requires require_admin
app.include_router(admin_router, prefix="/api/v1")


# ============================================
# HEALTH ENDPOINTS
# ============================================
@app.get("/")
async def root():
    return {"message": "NuruCare API is running", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    r = get_system_health_detail()
    base = {"status": "healthy" if r["success"] and r["data"]["database"]["ok"] else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat()}
    if r["success"]:
        base["details"] = r["data"]
    return base


# ============================================
# AUTH ENDPOINTS
# ============================================
@app.post("/api/v1/auth/signup")
async def signup(request: SignupRequest):
    """Public signup — creates patient OR nurse accounts. Patients are active
    immediately. Nurse signups are created with is_active=False and cannot log in
    until an existing admin activates them from the admin panel's user management
    screen (existing Activate/Deactivate control) — a self-service nurse account is
    still a privileged, patient-data-adjacent role, so it goes through a human
    review gate rather than being usable the instant the form is submitted. No
    access token is issued for a pending nurse signup, since the account cannot
    authenticate yet.

    Admin accounts are more privileged still and cannot be created or granted
    through any HTTP endpoint at all — the only path is the CLI bootstrap script
    (backend/scripts/create_admin.py), run directly against the deployment
    environment. Any role value other than 'patient'/'nurse' is rejected outright.
    """
    role = (request.role or "patient").strip().lower()
    if role not in ("patient", "nurse"):
        raise HTTPException(
            status_code=403,
            detail="Only patient or nurse accounts can be created via signup. Admin accounts are created via backend/scripts/create_admin.py.",
        )

    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isdigit() for c in request.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")

    if role == "nurse" and not (request.institution_name or "").strip():
        raise HTTPException(status_code=400, detail="Institution/facility name is required for healthcare provider accounts")

    existing_user = get_user_by_username(request.username)
    if existing_user["success"]:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = get_user_by_email(request.email)
    if existing_email["success"]:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = hash_password(request.password)
    is_nurse_signup = role == "nurse"

    result = create_user(
        username=request.username,
        email=request.email,
        password_hash=hashed_password,
        full_name=request.full_name,
        role=role,
        gender=request.gender,
        institution_name=request.institution_name,
        institution_address=request.institution_address,
        is_active=not is_nurse_signup,
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to create user"))

    if is_nurse_signup:
        return {
            "success": True,
            "pending_approval": True,
            "message": "Your healthcare provider account has been created and is pending review by a NuruCare administrator. You'll be able to sign in once it's activated.",
            "user_id": result["user_id"],
            "role": role,
        }

    token = create_access_token(
        {"sub": result["user_id"], "role": role, "name": request.full_name, "gender": request.gender}
    )

    return {
        "success": True,
        "pending_approval": False,
        "message": "Patient account created successfully",
        "user_id": result["user_id"],
        "access_token": token,
        "role": role,
    }


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login a user (patient, nurse, or admin) using username/password.
    Rejects deactivated accounts (is_active=false)."""
    user_result = get_user_by_username(request.username)
    if not user_result["success"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user = user_result["user"]
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is not active. If you just signed up as a healthcare provider, an admin needs to approve your account first. Otherwise, contact an admin.")

    token = create_access_token({
        "sub": str(user["user_id"]),
        "role": user["role"],
        "name": user.get("full_name"),
        "gender": user.get("gender"),
    })
    return TokenResponse(
        access_token=token,
        role=user["role"],
        name=user.get("full_name"),
        gender=user.get("gender"),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@app.post("/api/v1/auth/nurse/login", response_model=TokenResponse)
async def nurse_login(request: NurseLoginRequest):
    """Nurse login with username + password → JWT.
    Uses DB-backed users first (role=nurse). Deactivated accounts are rejected.
    The legacy hardcoded NURSE_ACCOUNTS fallback is retained as a last-resort escape hatch
    so an admin locked out of DB access can still get in — but it is only consulted when
    no matching DB user exists at all, not when a DB user has the wrong password.
    """
    user_result = get_user_by_username(request.username)
    if user_result["success"]:
        user = user_result["user"]
        if not user.get("is_active", True):
            raise HTTPException(status_code=403, detail="Account is not active. If you just signed up as a healthcare provider, an admin needs to approve your account first. Otherwise, contact an admin.")
        if verify_password(request.password, user["password_hash"]) and user["role"] == "nurse":
            token = create_access_token({
                "sub": str(user["user_id"]),
                "role": user["role"],
                "name": user.get("full_name"),
                "gender": user.get("gender"),
            })
            return TokenResponse(
                access_token=token,
                role=user["role"],
                name=user.get("full_name"),
                gender=user.get("gender"),
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )
        raise HTTPException(status_code=401, detail="Invalid username or password")

    from auth import NURSE_ACCOUNTS, DEMO_MODE
    if not DEMO_MODE:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    account = NURSE_ACCOUNTS.get(request.username)
    if account and account["password"] == request.password:
        token = create_access_token({"sub": request.username, "role": "nurse", "name": account["name"]})
        return TokenResponse(
            access_token=token,
            role="nurse",
            name=account["name"],
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/v1/auth/patient/session", response_model=PatientSessionResponse)
async def create_patient_session():
    """Create an anonymous patient session (user_id = None)."""
    result = save_intake_data(None, {
        "age": 0, "systolic_bp": 0, "diastolic_bp": 0,
        "smoking": False, "migraine_type": "none", "breastfeeding": False,
        "intake_channel": "web",
    }, user_id=None)
    if not result["success"]:
        raise HTTPException(status_code=500, detail="Failed to create session")

    profile_id = result["profile_id"]
    token = create_access_token({"sub": profile_id, "role": "patient"}, expires_minutes=60 * 24)
    return PatientSessionResponse(profile_id=profile_id, access_token=token)

@app.get("/api/v1/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Return current authenticated user info"""
    return {
        "sub": user.get("sub"),
        "role": user.get("role"),
        "name": user.get("name"),
        "gender": user.get("gender"),
    }


# ============================================
# INTAKE & RECOMMENDATIONS
# ============================================
@app.post("/api/v1/intake")
async def submit_intake(intake_data: IntakeData, user: Optional[dict] = Depends(optional_auth)):
    """Save full intake data. For authenticated patients the profile_id AND user_id
    are both set so JOINs work correctly (p.user_id = u.user_id. For anonymous
    patients user_id is NULL as expected.
    """
    is_authed_patient = user and user.get("role") == "patient"
    profile_id = user.get("sub") if is_authed_patient else None
    explicit_user_id = user.get("sub") if is_authed_patient else None
    result = save_intake_data(profile_id, intake_data.dict(), user_id=explicit_user_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to save intake"))
    return {"success": True, "message": "Intake data received", "profile_id": result["profile_id"]}

@app.get("/api/v1/patient/profile")
async def get_patient_profile(user: dict = Depends(get_current_user)):
    """Get current patient's profile with computed safety score."""
    if user.get("role") != "patient":
        raise HTTPException(status_code=403, detail="Patient access required")
    profile_id = user.get("sub")
    result = get_profile_by_id(profile_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = result["data"]
    score_bundle = compute_safety_score(profile)
    return {
        "success": True,
        "profile": profile,
        "safety_score": score_bundle,
    }


class PatientProfileUpdate(BaseModel):
    side_effects: Optional[list] = None
    duration_pref: Optional[str] = None
    last_period_date: Optional[str] = None
    postpartum_weeks: Optional[int] = None
    breastfeeding: Optional[bool] = None
    smoking: Optional[bool] = None
    migraine_type: Optional[str] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    age: Optional[int] = None


@app.put("/api/v1/patient/profile")
async def update_patient_profile(
    payload: PatientProfileUpdate,
    user: dict = Depends(get_current_user),
):
    """Partial update of the patient's profile (e.g. to log new side effects)."""
    if user.get("role") != "patient":
        raise HTTPException(status_code=403, detail="Patient access required")
    profile_id = user.get("sub")
    patch = payload.model_dump(exclude_unset=True)
    result = update_profile_fields(profile_id, patch)
    if not result["success"]:
        raise HTTPException(status_code=400 if "fields" in result["error"].lower() else 404, detail=result.get("error"))
    updated = result["data"]
    return {
        "success": True,
        "profile": updated,
        "safety_score": compute_safety_score(updated),
    }


@app.post("/api/v1/patient/profile/side-effects")
async def append_side_effect_log(
    payload: dict,
    user: dict = Depends(get_current_user),
):
    """Append a single side-effect entry to the side_effects jsonb array.
    payload: { symptom, severity, started_on, notes?, method? }
    """
    if user.get("role") != "patient":
        raise HTTPException(status_code=403, detail="Patient access required")
    profile_id = user.get("sub")
    existing_profile = get_profile_by_id(profile_id)
    if not existing_profile["success"]:
        raise HTTPException(status_code=404, detail="Profile not found")
    current = existing_profile["data"].get("side_effects") or []
    if not isinstance(current, list):
        current = []
    entry = {
        "id": payload.get("id") or ("se_" + secrets.token_hex(5)),
        "symptom": payload.get("symptom"),
        "severity": payload.get("severity", "mild"),
        "started_on": payload.get("started_on") or datetime.now(timezone.utc).date().isoformat(),
        "notes": payload.get("notes") or "",
        "method": payload.get("method") or "",
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    next_list = current + [entry]
    saved = update_profile_fields(profile_id, {"side_effects": next_list})
    if not saved["success"]:
        raise HTTPException(status_code=500, detail=saved.get("error"))
    return {"success": True, "side_effects": next_list, "entry": entry}

@app.post("/api/v1/recommend")
async def get_recommendations(intake_data: IntakeData):
    """Get contraceptive recommendations using the unified WHO MEC guardrail +
    recommendation pipeline (the same engine used by the USSD flow). Replaces the
    legacy hardcoded age-band implementation so web and USSD share one engine.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    pipeline = _get_recommendation_pipeline()
    profile = _map_intake_to_pipeline(intake_data)

    try:
        result = pipeline.recommend(profile)
    except Exception as exc:
        print(
            f"[FATAL] Recommendation pipeline failed ({exc}). Returning a safe, "
            "conservative empty response: no recommendations listed, provider "
            "consultation required."
        )
        from engine.guardrail import WHOMECGuardrail
        try:
            guardrail = WHOMECGuardrail()
            gr = guardrail.evaluate(profile)
            # guardrail.restricted_methods is a dict {method_id: category_int} and
            # explanations is a list of {rule_id, explanation}. Convert to the same
            # list-of-dicts shape the pipeline produces so formatters work.
            native_restricted = gr.get("restricted_methods") or {}
            native_explanations = (gr.get("explanations") or [])
            explanations_by_method = {}
            for ex in native_explanations:
                if isinstance(ex, dict):
                    explanations_by_method[ex.get("rule_id")] = ex.get("explanation")
            translated_restrictions = []
            for method_id, category in native_restricted.items():
                mid_human = method_id.replace("_", " ").title()
                translated_restrictions.append({
                    "method_id": method_id,
                    "method_name": mid_human,
                    "category": category,
                    "explanation": explanations_by_method.get(method_id, "Contraindicated for this profile per WHO MEC rules."),
                    "rule_id": method_id,
                })
            result = {
                "recommended_methods": [],
                "restricted_methods": translated_restrictions,
                "requires_provider": bool(gr.get("requires_provider", True)),
                "allowed_count": len(gr.get("allowed_methods", [])),
                "restricted_count": len(translated_restrictions),
                "timestamp": datetime.now().isoformat(),
                "disclaimer": "Engine fallback: no ranked methods provided. Consult a healthcare provider.",
            }
        except Exception as exc2:
            print(f"[FATAL] Guardrail fallback ALSO failed ({exc2}). Returning fully empty safe response.")
            result = {
                "recommended_methods": [],
                "restricted_methods": [],
                "requires_provider": True,
                "timestamp": datetime.now().isoformat(),
                "disclaimer": "System degraded. You MUST consult a healthcare provider before choosing a method.",
            }

    formatted_recommended = _format_recommended_for_api(result.get("recommended_methods"))
    formatted_restricted = _format_restricted_for_api(result.get("restricted_methods"))

    # Build a concise summary for the AI narrative field, falling back to the
    # real ai_client if Gemini is configured (see ai_client.py for env checks).
    base_summary_parts = []
    for m in formatted_recommended[:3]:
        if m.get("explanation"):
            base_summary_parts.append(f"• {m['name']}: {m['explanation']}")
    narrative_summary = "\n".join(base_summary_parts) if base_summary_parts else result.get("summary", "")
    disclaimer = result.get("disclaimer", "Always consult a healthcare provider before starting any contraceptive method.")

    loop = asyncio.get_event_loop()
    try:
        with ThreadPoolExecutor() as pool:
            swahili_version, full_ai = await asyncio.gather(
                loop.run_in_executor(pool, translate_to_swahili, narrative_summary),
                loop.run_in_executor(pool, get_ai_recommendation, intake_data.model_dump(), narrative_summary, disclaimer),
            )
    except Exception as exc:
        # The clinically important part (formatted_recommended/formatted_restricted,
        # computed above via the real WHO MEC pipeline) is already safe at this
        # point. Narrative/translation text is a presentation nicety on top of
        # that — a bug here should degrade to plain English text, never crash
        # the whole /recommend response and block the patient from seeing their
        # actual (already-correct) recommendations.
        print(f"[ERROR] AI narrative/translation step failed ({exc}). Falling back to plain summary text.")
        swahili_version = narrative_summary
        full_ai = narrative_summary or disclaimer

    return {
        "recommended_methods": formatted_recommended,
        "restricted_methods": formatted_restricted,
        "requires_provider_consultation": bool(result.get("requires_provider", formatted_restricted)),
        "general_advice": disclaimer,
        "timestamp": result.get("timestamp", datetime.now().isoformat()),
        "swahili_version": swahili_version,
        "full_ai_response": full_ai,
        "engine_meta": {
            "from_pipeline": True,
            "allowed_count": result.get("allowed_count"),
            "restricted_count": result.get("restricted_count"),
            "summary": result.get("summary"),
        },
    }


# ============================================
# NURSE SESSION KEYS
# ============================================
@app.post("/api/v1/session-key")
async def generate_session_key(request: SessionKeyRequest, user: Optional[dict] = Depends(optional_auth)):
    """Patient generates a 6-digit code to share with nurse"""
    profile_id = request.profile_id
    is_authed_patient = user and user.get("role") == "patient"
    if not profile_id and is_authed_patient:
        profile_id = user.get("sub")

    if not profile_id:
        created = save_intake_data(None, {
            "age": 0, "systolic_bp": 0, "diastolic_bp": 0,
            "smoking": False, "migraine_type": "none", "breastfeeding": False,
            "intake_channel": "web",
        }, user_id=None)
        if not created["success"]:
            raise HTTPException(status_code=500, detail="Failed to create anonymous profile")
        profile_id = created["profile_id"]

    session_key = ''.join(secrets.choice(string.digits) for _ in range(6))
    result = save_session_key(session_key, profile_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate session key"))

    return {"session_key": session_key, "profile_id": profile_id, "expires_in_minutes": 15}

@app.post("/api/v1/nurse/verify-session")
async def nurse_verify_session(
    request: NurseVerifySessionRequest,
    nurse: dict = Depends(require_nurse),
):
    """Nurse enters 6-digit code → gets patient profile. Nurse JWT required.
    Rate-limited per access code (5 attempts / 60s) to block brute force.
    """
    result = rate_limited_verify_session_key(request.session_key)
    if not result["success"]:
        status = 429 if "Too many attempts" in result.get("error", "") else 400
        raise HTTPException(status_code=status, detail=result.get("error", "Invalid or expired session key"))

    profile = get_profile_by_id(result["patient_id"])
    if not profile["success"]:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    return {"success": True, "patient_data": profile["data"]}


# ============================================
# PARTNER SYNC
# ============================================
@app.post("/api/v1/sync/token")
async def generate_sync_token(request: SyncGenerateRequest, user: Optional[dict] = Depends(optional_auth)):
    """Generate anonymous partner sync token"""
    profile_id = request.profile_id
    is_authed_patient = user and user.get("role") == "patient"
    if not profile_id and is_authed_patient:
        profile_id = user.get("sub")

    if not profile_id:
        created = save_intake_data(None, {
            "age": 0, "systolic_bp": 0, "diastolic_bp": 0,
            "smoking": False, "migraine_type": "none", "breastfeeding": False,
            "intake_channel": "web",
        }, user_id=None)
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
    """Partner enters the sync token → profiles are linked.
    Rate-limited per token (10 attempts / 60s) as anti-spray.
    """
    result = rate_limited_verify_sync_token(request.token)
    if not result["success"]:
        status = 429 if "Too many attempts" in result.get("error", "") else 400
        raise HTTPException(status_code=status, detail=result.get("error", "Invalid or expired token"))

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


# ============================================
# NURSE DASHBOARD (protected)
# ============================================
@app.get("/api/v1/nurse/dashboard")
async def get_dashboard(nurse: dict = Depends(require_nurse)):
    """Fetch dashboard stats nurse JWT required"""
    result = get_dashboard_data()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result["data"]


# ============================================
# TRANSLATION UTILITY
# ============================================
@app.post("/api/v1/translate")
async def translate_text(request: TranslateRequest):
    translation = translate_to_swahili(request.text)
    return {"original": request.text, "translated": translation, "language": request.target_language}


# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)