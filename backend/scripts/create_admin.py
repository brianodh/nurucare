"""
Bootstrap an admin account (interactive CLI — the ONLY supported way to
create an admin user in NuruCare).

Usage (from backend/ directory):
  python -m scripts.create_admin

Why this exists as a standalone script rather than an API endpoint:
Admin accounts are never created or promoted over HTTP, by anyone, under any
circumstance -- not via signup, not via the admin panel's role-update
endpoint (see api/endpoints/admin.py: admin_update_role explicitly rejects
new_role="admin"), not via database.update_user_role (same rejection at the
DB layer as defense in depth). The only path to `role = 'admin'` is running
this script with real shell/CLI access to the backend environment.

This mirrors scripts/seed_demo_nurses.py's conventions (path setup, reuse of
auth.hash_password + database.create_user / get_user_by_username /
get_user_by_email) but is interactive and password-confirming, since it's
meant to be run by hand, deliberately, by someone with deploy access -- not
auto-run as part of a seed/demo flow.
"""

from __future__ import annotations

import getpass
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import hash_password
from database import create_user, get_user_by_username, get_user_by_email


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _prompt_non_empty(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("  This field is required.")


def _prompt_email() -> str:
    while True:
        value = input("Admin email: ").strip().lower()
        if EMAIL_RE.match(value):
            return value
        print("  Please enter a valid email address.")


def _prompt_username(default_from_email: str) -> str:
    suggested = default_from_email.split("@")[0]
    value = input(f"Username [{suggested}]: ").strip()
    return value or suggested


def _prompt_password() -> str:
    while True:
        password = getpass.getpass("Password (min 12 chars, at least 1 number): ")
        if len(password) < 12:
            print("  Admin passwords must be at least 12 characters. Try again.")
            continue
        if not any(c.isdigit() for c in password):
            print("  Admin passwords must contain at least one number. Try again.")
            continue
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("  Passwords do not match. Try again.")
            continue
        return password


def main() -> int:
    print("=" * 62)
    print("  NuruCare -- Admin Account Bootstrap (CLI-only, by design)")
    print("=" * 62)
    print(
        "This is the ONLY way to create an admin account. There is no API\n"
        "or in-app path to role='admin' anywhere in this application.\n"
    )

    email = _prompt_email()
    if get_user_by_email(email)["success"]:
        print(f"\n[FAILED] A user with email '{email}' already exists. Aborting.")
        return 1

    username = _prompt_username(email)
    if get_user_by_username(username)["success"]:
        print(f"\n[FAILED] A user with username '{username}' already exists. Aborting.")
        return 1

    full_name = _prompt_non_empty("Full name")
    password = _prompt_password()

    print(f"\nAbout to create ADMIN account:")
    print(f"  username : {username}")
    print(f"  email    : {email}")
    print(f"  name     : {full_name}")
    confirm = input("Proceed? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted -- no account created.")
        return 1

    password_hash = hash_password(password)
    result = create_user(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role="admin",
        gender=None,
        institution_name=None,
        institution_address=None,
    )

    if not result["success"]:
        print(f"\n[FAILED] Could not create admin account: {result.get('error')}")
        return 1

    print(f"\n[OK] Admin account created (user_id={result['user_id']}).")
    print(f"     {username} can now log in at /login like any other account --")
    print("     Login.jsx already routes role='admin' to /admin/dashboard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())