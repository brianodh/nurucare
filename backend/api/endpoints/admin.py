"""
NuruCare Admin Endpoints
All endpoints require require_admin dependency.
Every figure is a live DB query — no seed/demo numbers.
"""

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr

from database import (
    get_admin_overview_stats,
    get_admin_signup_trend,
    list_content_items,
    get_content_item,
    upsert_content_item,
    delete_content_item,
    list_all_users,
    get_user_by_id_admin,
    update_user_role,
    toggle_user_active,
    create_user,
    get_nurse_session_monitor,
    force_expire_nurse_session,
    get_partner_sync_monitor,
    get_system_health_detail,
    get_user_by_username,
)
from auth import require_admin, hash_password


router = APIRouter(prefix="/admin", tags=["Admin"])


# ================================================================
# REQUEST MODELS
# ================================================================

class ContentUpsertRequest(BaseModel):
    content_type: str
    item_key: str
    content_data: dict


class ContentDeleteRequest(BaseModel):
    content_type: str
    item_key: str


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "patient"
    gender: Optional[str] = None
    institution_name: Optional[str] = None
    institution_address: Optional[str] = None


class UpdateRoleRequest(BaseModel):
    user_id: str
    new_role: str


class ToggleActiveRequest(BaseModel):
    user_id: str
    is_active: bool


class ForceExpireSessionRequest(BaseModel):
    session_id: str


# ================================================================
# 1. PLATFORM OVERVIEW (Landing Tab)
# ================================================================

@router.get("/overview")
def admin_overview(admin: dict = Depends(require_admin)):
    """Live platform-wide counts and splits."""
    result = get_admin_overview_stats()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result["data"]


@router.get("/signup-trend")
def admin_signup_trend(
    days: int = Query(7, ge=1, le=90),
    admin: dict = Depends(require_admin),
):
    """Daily signup COUNT/GROUP BY for the last N days."""
    result = get_admin_signup_trend(days=days)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result["data"]


# ================================================================
# 2. KNOWLEDGE BASE / CONTENT MANAGER
# ================================================================

@router.get("/content")
def admin_list_content(
    content_type: Optional[str] = None,
    admin: dict = Depends(require_admin),
):
    """List content items (optionally filtered by type).
    If DB is empty, seeds from data/knowledge_base/*.json on first read."""
    result = list_content_items(content_type=content_type)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return {"items": result["data"]}


@router.get("/content/{content_type}/{item_key}")
def admin_get_content(
    content_type: str,
    item_key: str,
    admin: dict = Depends(require_admin),
):
    """Get a single content item."""
    result = get_content_item(content_type, item_key)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result["data"]


@router.post("/content")
def admin_upsert_content(
    payload: ContentUpsertRequest,
    admin: dict = Depends(require_admin),
):
    """Create or update a content item. Bumps version; records updated_by/updated_at."""
    result = upsert_content_item(
        payload.content_type,
        payload.item_key,
        payload.content_data,
        admin.get("sub"),
    )
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return {"success": True, "item": result["data"]}


@router.delete("/content")
def admin_delete_content(
    payload: ContentDeleteRequest,
    admin: dict = Depends(require_admin),
):
    """Delete a content item."""
    result = delete_content_item(payload.content_type, payload.item_key)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return {"success": True}


# ================================================================
# 3. WHO MEC RULES CONSOLE (read-only)
# ================================================================

@router.get("/who-mec-rules")
def admin_who_mec_rules(admin: dict = Depends(require_admin)):
    """Read-only view of engine/who_mec_rules.json plus guardrail.py summary.
    Lets admins see exactly what drives eligibility decisions."""
    rules_path = Path(__file__).parent.parent.parent / "engine" / "who_mec_rules.json"
    guardrail_path = Path(__file__).parent.parent.parent / "engine" / "guardrail.py"

    rules_data = None
    if rules_path.exists():
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                rules_data = json.load(f)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to load WHO MEC rules: {exc}")
    else:
        raise HTTPException(status_code=404, detail="WHO MEC rules file not found")

    guardrail_summary = None
    if guardrail_path.exists():
        try:
            src = guardrail_path.read_text(encoding="utf-8")
            guardrail_summary = {
                "file": str(guardrail_path.name),
                "size_bytes": len(src),
                "has_guardrail_class": "class WHOMECGuardrail" in src,
                "has_evaluate_method": "def evaluate" in src,
                "rules_count": len(rules_data.get("rules", [])) if rules_data else 0,
                "method_mapping_keys": list(rules_data.get("method_mapping", {}).keys()) if rules_data else [],
            }
        except Exception:
            guardrail_summary = {"error": "Could not read guardrail.py"}

    return {
        "rules": rules_data,
        "guardrail": guardrail_summary,
    }


# ================================================================
# 4. USER & ACCOUNT MANAGEMENT
# ================================================================

@router.get("/users")
def admin_list_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(200, ge=1, le=500),
    admin: dict = Depends(require_admin),
):
    """List/search all users. password_hash is never returned."""
    if role and role not in ("patient", "nurse", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role filter")
    result = list_all_users(role=role, search=search, limit=limit)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return {"users": result["data"]}


@router.get("/users/{user_id}")
def admin_get_user(user_id: str, admin: dict = Depends(require_admin)):
    """Get a single user by ID (no password_hash)."""
    result = get_user_by_id_admin(user_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result["data"]


@router.post("/users/create-nurse")
def admin_create_nurse(
    payload: CreateUserRequest,
    admin: dict = Depends(require_admin),
):
    """Admins create real nurse accounts directly in users table (bcrypt-hashed).
    Replaces the hardcoded NURSE_ACCOUNTS dict. Self-promotion to admin is blocked at create time.
    """
    if payload.role != "nurse":
        raise HTTPException(status_code=400, detail="This endpoint only creates nurse accounts. Use role=nurse.")
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isdigit() for c in payload.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")

    existing = get_user_by_username(payload.username)
    if existing["success"]:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = hash_password(payload.password)
    result = create_user(
        username=payload.username,
        email=payload.email,
        password_hash=hashed,
        full_name=payload.full_name,
        role="nurse",
        gender=payload.gender,
        institution_name=payload.institution_name,
        institution_address=payload.institution_address,
    )
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return {"success": True, "user_id": result["user_id"], "message": "Nurse account created"}


@router.post("/users/update-role")
def admin_update_role(
    payload: UpdateRoleRequest,
    admin: dict = Depends(require_admin),
):
    """Promote/demote a user role. Protects against self-promotion:
    actor (admin token sub) cannot change their own role via this endpoint.

    "admin" is not an accepted value here, even for an authenticated admin
    caller. Admin accounts are created exclusively via the CLI bootstrap script
    (backend/scripts/create_admin.py) -- there is no HTTP path to admin, by design.
    """
    if payload.new_role not in ("patient", "nurse"):
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be created or promoted via the API. Use backend/scripts/create_admin.py.",
        )
    actor_id = str(admin.get("sub", ""))
    if actor_id == str(payload.user_id):
        raise HTTPException(status_code=403, detail="Self-promotion/demotion is not allowed")
    result = update_user_role(payload.user_id, payload.new_role, actor_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return {"success": True, "updated": result["data"]}


@router.post("/users/toggle-active")
def admin_toggle_active(
    payload: ToggleActiveRequest,
    admin: dict = Depends(require_admin),
):
    """Deactivate or reactivate a user account."""
    actor_id = str(admin.get("sub", ""))
    if actor_id == str(payload.user_id):
        raise HTTPException(status_code=403, detail="You cannot deactivate your own account")
    result = toggle_user_active(payload.user_id, payload.is_active)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return {"success": True, "updated": result["data"]}


# ================================================================
# 5. SESSION & SYNC MONITORING
# ================================================================

@router.get("/monitor/nurse-sessions")
def admin_nurse_sessions(admin: dict = Depends(require_admin)):
    """Live nurse session code view: active/expired counts + list."""
    result = get_nurse_session_monitor()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result["data"]


@router.post("/monitor/nurse-sessions/force-expire")
def admin_force_expire_session(
    payload: ForceExpireSessionRequest,
    admin: dict = Depends(require_admin),
):
    """Immediately invalidate a nurse access code. Addresses 6-digit code abuse risk."""
    result = force_expire_nurse_session(payload.session_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return {"success": True, "session_id": payload.session_id}


@router.get("/monitor/partner-sync")
def admin_partner_sync(admin: dict = Depends(require_admin)):
    """Partner-sync token monitor: active/expired/used counts + list."""
    result = get_partner_sync_monitor()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result["data"]


# ================================================================
# 6. SYSTEM HEALTH
# ================================================================

@router.get("/health")
def admin_system_health(admin: dict = Depends(require_admin)):
    """Extended system health for admins: DB, Gemini API key state,
    recommendation engine path, entrypoint confirmation."""
    result = get_system_health_detail()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result["data"]