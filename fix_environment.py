"""
Environment Fix Script for NuruCare
Run this to test and fix PostgreSQL and Gemini connections
"""

import os
import sys
import subprocess

print("=" * 70)
print("🔧 NURUCARE - ENVIRONMENT DIAGNOSTIC TOOL")
print("=" * 70)

# =========================================================
# 1. CHECK POSTGRESQL
# =========================================================
print("\n📊 1. CHECKING POSTGRESQL CONNECTION")
print("-" * 50)

# Try different passwords
passwords_to_try = ['postgres', 'password', 'admin', '']
connected = False

for pwd in passwords_to_try:
    try:
        import psycopg
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=pwd,
            database="postgres"
        )
        conn.close()
        print(f"   ✅ Connected! Password is: '{pwd}'")
        print(f"\n   Set this environment variable:")
        print(f"   set DATABASE_URL=postgresql://postgres:{pwd}@localhost:5432/nurucare")
        connected = True
        break
    except:
        continue

if not connected:
    print("   ❌ Could not connect to PostgreSQL")
    print("\n   Troubleshooting steps:")
    print("   1. Make sure PostgreSQL is installed")
    print("   2. Run: net start postgresql-x64-16")
    print("   3. Or reset your password using pgAdmin")

# =========================================================
# 2. CHECK GEMINI API
# =========================================================
print("\n🤖 2. CHECKING GEMINI API")
print("-" * 50)

gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print(f"   ✅ GEMINI_API_KEY is set (starts with {gemini_key[:10]}...)")
    
    # Test the API
    try:
        from google import genai
        client = genai.Client(api_key=gemini_key)
        print("   ✅ Google GenAI client created successfully")
        
        # Quick test
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Say 'API works'"
        )
        print(f"   ✅ API test response: {response.text[:50]}...")
        
    except ImportError:
        print("   ❌ google-genai not installed. Run: pip install google-genai")
    except Exception as e:
        print(f"   ❌ API error: {e}")
else:
    print("   ❌ GEMINI_API_KEY not set")
    print("\n   To fix:")
    print("   1. Go to https://aistudio.google.com/")
    print("   2. Click 'Get API Key'")
    print("   3. Copy your key")
    print("   4. Run: set GEMINI_API_KEY=your_key_here")

# =========================================================
# 3. CHECK DATABASE TABLES
# =========================================================
print("\n🗄️ 3. CHECKING DATABASE TABLES")
print("-" * 50)

if connected:
    try:
        import psycopg
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=passwords_to_try[0] if connected else "",
            database="nurucare"
        )
        cur = conn.cursor()
        
        tables = ['who_guidelines', 'myths', 'educational_content']
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"   ✅ {table}: {count} records")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"   ❌ Error checking tables: {e}")
else:
    print("   ⚠️ Skipping (PostgreSQL not connected)")

print("\n" + "=" * 70)
print("📋 NEXT STEPS")
print("=" * 70)
print("""
1. Set DATABASE_URL environment variable:
   set DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/nurucare

2. Set GEMINI_API_KEY environment variable:
   set GEMINI_API_KEY=your_actual_api_key

3. Run the RAG pipeline again:
   python backend\engine\rag_pipeline.py
""")