"""
Seed demo nurse accounts into the users table (idempotent).

Usage (from backend/ directory):
  python -m scripts.seed_demo_nurses

Only inserts when DEMO_MODE=true (reads the env var directly) AND the
username does not already exist in users. This is safe to re-run and
idempotent.

Replaces the hardcoded NURSE_ACCOUNTS dict fallback in auth.py by
persisting the same two accounts as real users rows with bcrypt-hashed
passwords (rounds=12).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import hash_password
from database import create_user, get_user_by_username


DEMO_NURSES = [
    {
        "username": "nurse.demo",
        "email": "nurse.demo@nurucare.example",
        "password": "NuruCare2026",
        "full_name": "Demo Nurse",
        "role": "nurse",
        "gender": None,
        "institution_name": "NuruCare Demo Clinic",
        "institution_address": "123 Wellness Ave, Nairobi",
    },
    {
        "username": "dr.alex",
        "email": "dr.alex@nurucare.example",
        "password": "NuruCare2026",
        "full_name": "Dr. Alex Nuru",
        "role": "nurse",
        "gender": None,
        "institution_name": "NuruCare Regional Hospital",
        "institution_address": "456 Care Blvd, Kisumu",
    },
]


def seed_demo_nurses() -> list[dict]:
    demo_mode = os.getenv("DEMO_MODE", "").lower() in ("1", "true", "yes", "on")
    results = []
    if not demo_mode:
        print("[seed_demo_nurses] DEMO_MODE is off skipping seed.")
        return results

    for entry in DEMO_NURSES:
        existing = get_user_by_username(entry["username"])
        if existing["success"]:
            print(f"[seed_demo_nurses] user {entry['username']} already exists skipped.")
            results.append({"username": entry["username"], "status": "existed"})
            continue
        pw_hash = hash_password(entry["password"])
        created = create_user(
            username=entry["username"],
            email=entry["email"],
            password_hash=pw_hash,
            full_name=entry["full_name"],
            role=entry["role"],
            gender=entry["gender"],
            institution_name=entry["institution_name"],
            institution_address=entry["institution_address"],
        )
        status = "created" if created["success"] else f"failed:{created.get('error')}"
        print(f"[seed_demo_nurses] {entry['username']} -> {status}")
        results.append({"username": entry["username"], "status": status, "user_id": created.get("user_id")})
    return results


if __name__ == "__main__":
    seed_demo_nurses()
