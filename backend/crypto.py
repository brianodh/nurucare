import hashlib
import secrets
import time
from typing import Tuple

ACTIVE_NURSE_CODES: dict[str, dict[str, float]] = {}

SYNC_TOKEN_TTL_SECONDS = 15 * 60
NURSE_CODE_TTL_SECONDS = 15 * 60


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_partner_sync_token() -> Tuple[str, int]:
    seed = secrets.token_urlsafe(16)
    raw = f"partner-sync:{seed}:{int(time.time())}"
    token = _hash_text(raw)[:10]
    return token, SYNC_TOKEN_TTL_SECONDS // 60


def generate_nurse_session_key() -> Tuple[str, int]:
    code = f"{secrets.randbelow(10**6):06d}"
    expires_at = time.time() + NURSE_CODE_TTL_SECONDS
    ACTIVE_NURSE_CODES[code] = {"expires_at": expires_at, "used": False}
    return code, NURSE_CODE_TTL_SECONDS // 60


def validate_nurse_session_key(code: str) -> bool:
    record = ACTIVE_NURSE_CODES.get(code)
    if not record:
        return False
    if record["used"]:
        return False
    if time.time() > record["expires_at"]:
        return False
    record["used"] = True
    return True


def cleanup_expired_nurse_codes() -> None:
    now = time.time()
    expired = [k for k, v in ACTIVE_NURSE_CODES.items() if now > v["expires_at"]]
    for key in expired:
        del ACTIVE_NURSE_CODES[key]
