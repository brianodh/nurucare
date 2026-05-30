"""
Test script for verifying pgvector setup
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import test_connection, init_db, get_db
from db.database import WHOGuideline, Myth, EducationalContent
from sqlalchemy import text

def test_pgvector():
    """Test that pgvector extension is installed and working"""
    print("=" * 60)
    print("TESTING PGVECTOR SETUP")
    print("=" * 60)
    
    # Test connection
    print("\n1. Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed")
        return False
    print("   ✅ Connection successful")
    
    # Test pgvector extension
    print("\n2. Testing pgvector extension...")
    db = next(get_db())
    try:
        result = db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
        if result.fetchone():
            print("   ✅ pgvector extension is installed")
        else:
            print("   ❌ pgvector extension not found")
            return False
    except Exception as e:
        print(f"   ❌ Error checking extension: {e}")
        return False
    
    # Test vector column creation
    print("\n3. Testing vector column support...")
    try:
        # Create a test table with vector column
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS test_vector (
                id SERIAL PRIMARY KEY,
                embedding vector(3)
            )
        """))
        db.commit()
        print("   ✅ Vector column created successfully")
        
        # Insert a test vector
        db.execute(text("""
            INSERT INTO test_vector (embedding) VALUES ('[1,2,3]')
        """))
        db.commit()
        print("   ✅ Vector insertion successful")
        
        # Drop test table
        db.execute(text("DROP TABLE test_vector"))
        db.commit()
        print("   ✅ Test table cleaned up")
        
    except Exception as e:
        print(f"   ❌ Vector operation failed: {e}")
        return False
    
    # Test vector similarity search
    print("\n4. Testing vector similarity search...")
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS test_similarity (
                id SERIAL PRIMARY KEY,
                embedding vector(3)
            )
        """))
        
        # Insert test vectors
        db.execute(text("INSERT INTO test_similarity (embedding) VALUES ('[1,0,0]')"))
        db.execute(text("INSERT INTO test_similarity (embedding) VALUES ('[0,1,0]')"))
        db.execute(text("INSERT INTO test_similarity (embedding) VALUES ('[0,0,1]')"))
        db.commit()
        
        # Search for similar vectors
        result = db.execute(text("""
            SELECT id, embedding <-> '[1,0.1,0]' as distance
            FROM test_similarity
            ORDER BY distance
            LIMIT 1
        """))
        closest = result.fetchone()
        print(f"   ✅ Similarity search successful (closest ID: {closest[0]})")
        
        # Clean up
        db.execute(text("DROP TABLE test_similarity"))
        db.commit()
        
    except Exception as e:
        print(f"   ❌ Similarity search failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL PGVECTOR TESTS PASSED!")
    print("=" * 60)
    print("\nYour vector database is ready for RAG integration!")
    
    return True


def check_tables():
    """Check that all required tables exist"""
    print("\n" + "=" * 60)
    print("CHECKING DATABASE TABLES")
    print("=" * 60)
    
    db = next(get_db())
    
    tables = ['who_guidelines', 'myths', 'educational_content', 'user_sessions', 'query_log']
    
    for table in tables:
        try:
            result = db.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"))
            exists = result.fetchone()[0]
            if exists:
                print(f"   ✅ {table} exists")
            else:
                print(f"   ❌ {table} does not exist")
        except Exception as e:
            print(f"   ❌ Error checking {table}: {e}")


if __name__ == "__main__":
    # Run tests
    success = test_pgvector()
    
    if success:
        # Check tables
        check_tables()
        
        print("\n" + "=" * 60)
        print("📋 NEXT STEPS")
        print("=" * 60)
        print("""
        1. Run the RAG pipeline to create embeddings
        2. Insert WHO guidelines into who_guidelines table
        3. Insert myths into myths table
        4. Insert educational content into educational_content table
        5. Use similarity_search() in your API endpoints
        """)
    else:
        print("\n❌ Please fix the issues above before proceeding.")