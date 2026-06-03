"""
Recreate Database Tables with New Vector Dimension
Run: python recreate_tables.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__) / "backend"))

try:
    from backend.db.database import init_db, engine
    from backend.db.database import Base
    
    print("=" * 60)
    print("🔄 RECREATING DATABASE TABLES")
    print("=" * 60)
    
    # Drop all existing tables
    print("\n📌 Dropping existing tables...")
    Base.metadata.drop_all(engine)
    print("   ✅ Tables dropped")
    
    # Create new tables with updated schema
    print("\n📌 Creating new tables with dimension 768...")
    init_db()
    print("   ✅ Tables created")
    
    print("\n" + "=" * 60)
    print("✅ Database tables recreated successfully!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("   1. PostgreSQL is running")
    print("   2. Database connection is correct")
    print("   3. You've updated Vector(384) to Vector(768) in database.py")