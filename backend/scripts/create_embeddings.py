"""
Create Embeddings and Insert into Vector Database
Using 3072 dimensions for compatibility
"""

import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import get_db
from db.database import WHOGuideline, Myth, EducationalContent

# ============================================
# CONFIGURATION
# ============================================

KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge_base"
WHO_GUIDELINES_FILE = KNOWLEDGE_BASE_DIR / "who_guidelines.json"
MYTHS_FILE = KNOWLEDGE_BASE_DIR / "myths.json"
EDUCATIONAL_CONTENT_FILE = KNOWLEDGE_BASE_DIR / "educational_content.json"

# Use 3072 dimensions for compatibility
EMBEDDING_DIMENSION = 3072


def create_fallback_embedding(text: str, dimension: int = 3072) -> List[float]:
    """Deterministic fallback embedding"""
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()

    embedding = []
    for i in range(dimension):
        val = (int(hash_hex[i % len(hash_hex)], 16) / 8) - 1
        embedding.append(val)
    return embedding


def create_embedding(text: str) -> List[float]:
    """Create embedding using fallback"""
    return create_fallback_embedding(text, dimension=EMBEDDING_DIMENSION)


def insert_who_guidelines(db):
    """Insert WHO guidelines"""
    print("\n" + "=" * 60)
    print("📚 INSERTING WHO GUIDELINES")
    print("=" * 60)

    with open(WHO_GUIDELINES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    guidelines = data.get('guidelines', [])
    print(f"📄 Found {len(guidelines)} WHO guidelines")

    inserted = 0
    for i, guideline in enumerate(guidelines):
        print(f"\n[{i+1}/{len(guidelines)}] Processing: {guideline.get('title', 'Unknown')[:50]}...")

        text_to_embed = f"""
Title: {guideline.get('title', '')}
Category: {guideline.get('category', '')}
Content: {guideline.get('content', '')}
"""

        embedding = create_embedding(text_to_embed)

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

        time.sleep(0.1)

    db.commit()
    print(f"\n✅ Inserted {inserted} WHO guidelines")
    return inserted


def insert_myths(db):
    """Insert myths"""
    print("\n" + "=" * 60)
    print("📖 INSERTING MYTHS")
    print("=" * 60)

    with open(MYTHS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    myths = data.get('myths', [])
    print(f"📄 Found {len(myths)} myths")

    inserted = 0
    for i, myth in enumerate(myths):
        print(f"\n[{i+1}/{len(myths)}] Processing: {myth.get('myth_statement', 'Unknown')[:50]}...")

        text_to_embed = f"""
Myth: {myth.get('myth_statement', '')}
Truth: {myth.get('truth_statement', '')}
Explanation: {myth.get('explanation', '')}
"""

        embedding = create_embedding(text_to_embed)

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

        time.sleep(0.1)

    db.commit()
    print(f"\n✅ Inserted {inserted} myths")
    return inserted


def insert_educational_content(db):
    """Insert educational content"""
    print("\n" + "=" * 60)
    print("🎓 INSERTING EDUCATIONAL CONTENT")
    print("=" * 60)

    with open(EDUCATIONAL_CONTENT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    methods = data.get('methods', [])
    print(f"📄 Found {len(methods)} methods")

    inserted = 0
    for i, method in enumerate(methods):
        print(f"\n[{i+1}/{len(methods)}] Processing: {method.get('name', 'Unknown')}...")

        benefits_text = '; '.join(method.get('benefits', []))
        side_effects_text = '; '.join(method.get('side_effects', []))

        text_to_embed = f"""
Method: {method.get('name', '')}
Benefits: {benefits_text}
Side Effects: {side_effects_text}
"""

        embedding = create_embedding(text_to_embed)

        content_id = f"METHOD_{method.get('method_id', f'UNKNOWN_{i}').upper()}"

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

        time.sleep(0.1)

    db.commit()
    print(f"\n✅ Inserted {inserted} educational content items")
    return inserted


def verify_insertion(db):
    """Verify insertion"""
    print("\n" + "=" * 60)
    print("🔍 VERIFYING DATABASE INSERTION")
    print("=" * 60)

    guideline_count = db.query(WHOGuideline).count()
    myth_count = db.query(Myth).count()
    content_count = db.query(EducationalContent).count()

    print(f"\n📊 Database counts:")
    print(f"   - WHO Guidelines: {guideline_count}")
    print(f"   - Myths: {myth_count}")
    print(f"   - Educational Content: {content_count}")

    return guideline_count, myth_count, content_count


def main():
    print("=" * 70)
    print("🚀 NURUCARE - VECTOR DATABASE POPULATION")
    print(f"📐 Using {EMBEDDING_DIMENSION} dimensions")
    print("=" * 70)

    print("\n📁 Checking knowledge base files...")
    for file_path in [WHO_GUIDELINES_FILE, MYTHS_FILE, EDUCATIONAL_CONTENT_FILE]:
        if file_path.exists():
            print(f"   ✅ {file_path.name}")
        else:
            print(f"   ❌ {file_path.name} - NOT FOUND")

    db = next(get_db())

    try:
        guideline_count = insert_who_guidelines(db)
        myth_count = insert_myths(db)
        content_count = insert_educational_content(db)
        verify_insertion(db)

        print("\n" + "=" * 70)
        print("✅ VECTOR DATABASE POPULATION COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Final Statistics:")
        print(f"   - WHO Guidelines: {guideline_count}")
        print(f"   - Myths: {myth_count}")
        print(f"   - Educational Content: {content_count}")
        print(f"   - Total records: {guideline_count + myth_count + content_count}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()