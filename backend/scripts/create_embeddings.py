"""
Create Embeddings and Insert into Vector Database
==================================================

This script:
1. Loads WHO guidelines, myths, and educational content from JSON files
2. Creates vector embeddings using Gemini Flash API
3. Inserts the embedded content into the pgvector database

Run: python backend/scripts/create_embeddings.py
"""

import sys
import os
import json
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================
# LOAD GEMINI API (with fallback for testing)
# ============================================

# Try to import Gemini (may fail if not installed)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("⚠️ Google Generative AI not installed. Run: pip install google-generativeai")
    GEMINI_AVAILABLE = False

# Import database modules
try:
    from db.database import get_db
    from db.database import WHOGuideline, Myth, EducationalContent
    DB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Database import error: {e}")
    DB_AVAILABLE = False


# ============================================
# CONFIGURATION
# ============================================

# Load Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Paths to knowledge base files
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge_base"
WHO_GUIDELINES_FILE = KNOWLEDGE_BASE_DIR / "who_guidelines.json"
MYTHS_FILE = KNOWLEDGE_BASE_DIR / "myths.json"
EDUCATIONAL_CONTENT_FILE = KNOWLEDGE_BASE_DIR / "educational_content.json"


# ============================================
# FALLBACK EMBEDDING (for testing without API)
# ============================================

def create_fallback_embedding(text: str, dimension: int = 384) -> list:
    """
    Create a deterministic fallback embedding for testing
    This is NOT for production - just for testing the database insertion
    
    Args:
        text: The text to "embed" (not actually used for meaningful vectors)
        dimension: Size of the embedding vector
        
    Returns:
        List of random-looking but deterministic floats
    """
    import hashlib
    
    # Create a hash of the text
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Generate deterministic "random" numbers
    embedding = []
    for i in range(dimension):
        # Use hash to generate a number between -1 and 1
        val = (int(hash_hex[i % len(hash_hex)], 16) / 8) - 1
        embedding.append(val)
    
    return embedding


def create_embedding(text: str) -> list:
    """
    Create a vector embedding from text using Gemini Flash API
    Falls back to deterministic embedding if API not available
    
    Args:
        text: The text to embed
        
    Returns:
        List of floats (embedding vector)
    """
    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            embedding_model = "models/embedding-001"
            result = genai.embed_content(
                model=embedding_model,
                content=text[:2000],  # Limit text length
                task_type="retrieval_document"
            )
            print("   📡 Using Gemini API for embedding")
            return result['embedding']
        except Exception as e:
            print(f"   ⚠️ Gemini API error: {e}")
            print("   🔄 Falling back to deterministic embedding")
            return create_fallback_embedding(text)
    else:
        print("   🔄 Using fallback embedding (for testing)")
        return create_fallback_embedding(text)


# ============================================
# INSERT FUNCTIONS
# ============================================

def insert_who_guidelines(db):
    """Insert WHO guidelines into database with embeddings"""
    print("\n" + "=" * 60)
    print("📚 INSERTING WHO GUIDELINES")
    print("=" * 60)
    
    # Check if file exists
    if not WHO_GUIDELINES_FILE.exists():
        print(f"❌ File not found: {WHO_GUIDELINES_FILE}")
        print("   Please create the knowledge_base folder and add who_guidelines.json")
        return 0
    
    with open(WHO_GUIDELINES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    guidelines = data.get('guidelines', [])
    print(f"📄 Found {len(guidelines)} WHO guidelines")
    
    inserted = 0
    for i, guideline in enumerate(guidelines):
        print(f"\n[{i+1}/{len(guidelines)}] Processing: {guideline.get('title', 'Unknown')[:50]}...")
        
        # Create text for embedding
        text_to_embed = f"""
Title: {guideline.get('title', '')}
Category: {guideline.get('category', '')}
Content: {guideline.get('content', '')}
Recommended Alternatives: {', '.join(guideline.get('recommended_alternatives', []))}
"""
        
        # Create embedding
        embedding = create_embedding(text_to_embed)
        
        # Create new record
        new_guideline = WHOGuideline(
            guideline_id=guideline.get('id', f"GUIDELINE_{i}"),
            title=guideline.get('title', ''),
            content=guideline.get('content', ''),
            category=guideline.get('category', 'general'),
            embedding=embedding
        )
        db.add(new_guideline)
        inserted += 1
        print(f"   ✅ Added to database")
        
        # Small delay to avoid API rate limits
        time.sleep(0.2)
    
    db.commit()
    print(f"\n✅ Inserted {inserted} WHO guidelines")
    return inserted


def insert_myths(db):
    """Insert myths into database with embeddings"""
    print("\n" + "=" * 60)
    print("📖 INSERTING MYTHS")
    print("=" * 60)
    
    if not MYTHS_FILE.exists():
        print(f"❌ File not found: {MYTHS_FILE}")
        print("   Please create the knowledge_base folder and add myths.json")
        return 0
    
    with open(MYTHS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    myths = data.get('myths', [])
    print(f"📄 Found {len(myths)} myths")
    
    inserted = 0
    for i, myth in enumerate(myths):
        print(f"\n[{i+1}/{len(myths)}] Processing: {myth.get('myth_statement', 'Unknown')[:50]}...")
        
        # Create text for embedding
        text_to_embed = f"""
Myth: {myth.get('myth_statement', '')}
Truth: {myth.get('truth_statement', '')}
Explanation: {myth.get('explanation', '')}
Category: {myth.get('category', 'general')}
"""
        
        # Create embedding
        embedding = create_embedding(text_to_embed)
        
        # Create new record
        new_myth = Myth(
            myth_id=myth.get('id', f"MYTH_{i}"),
            myth_statement=myth.get('myth_statement', ''),
            truth_statement=myth.get('truth_statement', ''),
            explanation=myth.get('explanation', ''),
            source=myth.get('source', ''),
            category=myth.get('category', 'general'),
            embedding=embedding
        )
        db.add(new_myth)
        inserted += 1
        print(f"   ✅ Added to database")
        
        time.sleep(0.2)
    
    db.commit()
    print(f"\n✅ Inserted {inserted} myths")
    return inserted


def insert_educational_content(db):
    """Insert educational content into database with embeddings"""
    print("\n" + "=" * 60)
    print("🎓 INSERTING EDUCATIONAL CONTENT")
    print("=" * 60)
    
    if not EDUCATIONAL_CONTENT_FILE.exists():
        print(f"❌ File not found: {EDUCATIONAL_CONTENT_FILE}")
        print("   Please create the knowledge_base folder and add educational_content.json")
        return 0
    
    with open(EDUCATIONAL_CONTENT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    methods = data.get('methods', [])
    print(f"📄 Found {len(methods)} educational content items")
    
    inserted = 0
    for i, method in enumerate(methods):
        print(f"\n[{i+1}/{len(methods)}] Processing: {method.get('name', 'Unknown')}...")
        
        # Create text for embedding
        benefits_text = '; '.join(method.get('benefits', []))
        side_effects_text = '; '.join(method.get('side_effects', []))
        
        text_to_embed = f"""
Method: {method.get('name', '')}
Benefits: {benefits_text}
Side Effects: {side_effects_text}
Side Effect Management: {method.get('side_effect_management', '')}
Who Should Use: {method.get('who_should_use', '')}
Who Should Not Use: {method.get('who_should_not_use', '')}
"""
        
        # Create embedding
        embedding = create_embedding(text_to_embed)
        
        # Create content ID
        content_id = f"METHOD_{method.get('method_id', f'UNKNOWN_{i}').upper()}"
        
        # Create new record
        new_content = EducationalContent(
            content_id=content_id,
            title=method.get('name', ''),
            content=text_to_embed,
            content_type='method',
            method_name=method.get('name', ''),
            embedding=embedding
        )
        db.add(new_content)
        inserted += 1
        print(f"   ✅ Added to database")
        
        time.sleep(0.2)
    
    db.commit()
    print(f"\n✅ Inserted {inserted} educational content items")
    return inserted


# ============================================
# VERIFICATION FUNCTION
# ============================================

def verify_insertion(db):
    """Verify that data was inserted correctly"""
    print("\n" + "=" * 60)
    print("🔍 VERIFYING DATABASE INSERTION")
    print("=" * 60)
    
    # Count records
    guideline_count = db.query(WHOGuideline).count()
    myth_count = db.query(Myth).count()
    content_count = db.query(EducationalContent).count()
    
    print(f"\n📊 Database counts:")
    print(f"   - WHO Guidelines: {guideline_count}")
    print(f"   - Myths: {myth_count}")
    print(f"   - Educational Content: {content_count}")
    
    # Show sample of each
    if guideline_count > 0:
        sample = db.query(WHOGuideline).first()
        print(f"\n📚 Sample WHO Guideline:")
        print(f"   - ID: {sample.guideline_id}")
        print(f"   - Title: {sample.title[:50]}...")
        print(f"   - Embedding dimension: {len(sample.embedding)}")
    
    if myth_count > 0:
        sample = db.query(Myth).first()
        print(f"\n📖 Sample Myth:")
        print(f"   - ID: {sample.myth_id}")
        print(f"   - Myth: {sample.myth_statement[:50]}...")
    
    if content_count > 0:
        sample = db.query(EducationalContent).first()
        print(f"\n🎓 Sample Educational Content:")
        print(f"   - ID: {sample.content_id}")
        print(f"   - Title: {sample.title}")
    
    return guideline_count, myth_count, content_count


# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("=" * 70)
    print("🚀 NURUCARE - VECTOR DATABASE POPULATION")
    print("=" * 70)
    
    # Check database availability
    if not DB_AVAILABLE:
        print("\n❌ Database modules not available. Please check your setup.")
        print("   Make sure you have installed: pip install sqlalchemy psycopg2-binary pgvector")
        return
    
    # Check if knowledge base files exist
    print("\n📁 Checking knowledge base files...")
    files_to_check = [
        WHO_GUIDELINES_FILE,
        MYTHS_FILE,
        EDUCATIONAL_CONTENT_FILE
    ]
    
    for file_path in files_to_check:
        if file_path.exists():
            print(f"   ✅ {file_path.name}")
        else:
            print(f"   ❌ {file_path.name} - NOT FOUND")
            print(f"      Expected at: {file_path}")
    
    print("\n" + "=" * 60)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Insert all data
        guideline_count = insert_who_guidelines(db)
        myth_count = insert_myths(db)
        content_count = insert_educational_content(db)
        
        # Verify insertion
        verify_insertion(db)
        
        # Final summary
        print("\n" + "=" * 70)
        print("✅ VECTOR DATABASE POPULATION COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Final Statistics:")
        print(f"   - WHO Guidelines inserted: {guideline_count}")
        print(f"   - Myths inserted: {myth_count}")
        print(f"   - Educational Content inserted: {content_count}")
        print(f"   - Total records: {guideline_count + myth_count + content_count}")
        
        if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
            print("\n⚠️ NOTE: Using fallback embeddings (for testing only)")
            print("   For production, set GEMINI_API_KEY environment variable")
            print("   and install: pip install google-generativeai")
        
    except Exception as e:
        print(f"\n❌ Error during insertion: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()