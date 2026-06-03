"""
Partner Sync API Endpoints
==========================

Endpoints for partner synchronization:
- POST /api/sync/token - Generate sync token
- POST /api/sync/verify - Verify and link with partner
- POST /api/sync/session-key - Generate nurse session key
- POST /api/sync/session-key/verify - Verify nurse session key
- GET /api/sync/status - Check token status
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sync.partner_sync import CryptographicSyncManager

router = APIRouter(prefix="/api/sync", tags=["Partner Sync"])

# Initialize sync manager
sync_manager = CryptographicSyncManager()


# =========================================================
# REQUEST/ RESPONSE MODELS
# =========================================================

class GenerateTokenRequest(BaseModel):
    user_id: str


class VerifyTokenRequest(BaseModel):
    token: str
    partner_id: str


class GenerateSessionKeyRequest(BaseModel):
    session_id: str


class VerifySessionKeyRequest(BaseModel):
    key: str


class SyncResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    expires_in_hours: Optional[int] = None
    expires_in_minutes: Optional[int] = None
    original_user_id: Optional[str] = None
    session_id: Optional[str] = None


# =========================================================
# ENDPOINTS
# =========================================================

@router.post("/token", response_model=SyncResponse)
async def generate_sync_token(request: GenerateTokenRequest):
    """
    Generate a partner sync token.
    
    Returns a 10-character token (e.g., "NX-7K9-2M4") that expires in 24 hours.
    Only the cryptographic hash is stored - the raw token cannot be recovered.
    """
    result = sync_manager.create_partner_sync(request.user_id)
    
    return SyncResponse(
        success=result['success'],
        message=result['message'],
        token=result.get('token'),
        expires_in_hours=result.get('expires_in_hours')
    )


@router.post("/verify", response_model=SyncResponse)
async def verify_sync_token(request: VerifyTokenRequest):
    """
    Verify a partner sync token and link two users.
    
    This creates a cryptographic link between the token creator
    and the partner entering the token. No personal identifiers
    are stored - only the hash of the token.
    """
    result = sync_manager.verify_partner_sync(request.token, request.partner_id)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return SyncResponse(
        success=result['success'],
        message=result['message'],
        original_user_id=result.get('original_user_id')
    )


@router.post("/session-key", response_model=SyncResponse)
async def generate_session_key(request: GenerateSessionKeyRequest):
    """
    Generate a temporary session key for healthcare provider access.
    
    Returns a 6-digit numeric key that expires in 15 minutes.
    Used for secure, temporary access to patient data.
    """
    result = sync_manager.create_session_key(request.session_id)
    
    return SyncResponse(
        success=result['success'],
        message=result['message'],
        token=result.get('key'),
        expires_in_minutes=result.get('expires_in_minutes')
    )


@router.post("/session-key/verify", response_model=SyncResponse)
async def verify_session_key(request: VerifySessionKeyRequest):
    """
    Verify a session key for healthcare provider access.
    
    Grants temporary access to a patient's session data.
    The key is one-time use and expires after 15 minutes.
    """
    result = sync_manager.verify_session_key(request.key)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return SyncResponse(
        success=result['success'],
        message=result['message'],
        session_id=result.get('session_id')
    )


@router.get("/status/{token}")
async def get_token_status(token: str):
    """
    Check the status of a token (without using it).
    
    Returns whether the token is valid, expired, or used.
    """
    status = sync_manager.get_token_status(token)
    return status