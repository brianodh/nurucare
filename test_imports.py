
try:
    import sys
    sys.path.insert(0, '.')
    from backend import auth, database, main
    print("[SUCCESS] Imports okay!")
    print(" - Auth module imported")
    print(" - Database module imported")
    print(" - Main module imported")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())
