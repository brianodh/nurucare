"""
Database Connection Module for NuruCare
Handles connection to PostgreSQL with pgvector
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

# Database connection string
# Format: postgresql://username:password@host:port/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/nurucare"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ============================================
# DATABASE MODELS
# ============================================

class WHOGuideline(Base):
    """WHO Guidelines table - stores medical guidelines as vectors"""
    __tablename__ = "who_guidelines"
    
    id = Column(Integer, primary_key=True, index=True)
    guideline_id = Column(String(50), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    embedding = Column(Vector(384))  # 384 dimensions for OpenAI embeddings
    created_at = Column(DateTime, default=datetime.utcnow)


class Myth(Base):
    """Myths table - stores contraceptive and menstrual myths"""
    __tablename__ = "myths"
    
    id = Column(Integer, primary_key=True, index=True)
    myth_id = Column(String(50), unique=True, nullable=False)
    myth_statement = Column(Text, nullable=False)
    truth_statement = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    source = Column(String(200))
    category = Column(String(50))
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=datetime.utcnow)


class EducationalContent(Base):
    """Educational Content table - stores method benefits and side effects"""
    __tablename__ = "educational_content"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String(50), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50))
    method_name = Column(String(100))
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=datetime.utcnow)


class UserSession(Base):
    """User Sessions table - temporary storage"""
    __tablename__ = "user_sessions"
    
    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_data = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class QueryLog(Base):
    """Query Log table - for analytics and open science"""
    __tablename__ = "query_log"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    embedding = Column(Vector(384))
    retrieved_docs = Column(JSON)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def test_connection():
    """Test database connection"""
    try:
        connection = engine.connect()
        print("✅ Database connection successful")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# ============================================
# VECTOR OPERATIONS
# ============================================

def create_embedding(text: str) -> list:
    """
    Create a vector embedding from text using Gemini Flash API
    
    This will be implemented in the RAG pipeline
    """
    # Placeholder - actual embedding will use Gemini Flash
    # Returns a list of 384 floats
    pass


def similarity_search(query_embedding: list, table_name: str, db, limit: int = 5):
    """
    Perform similarity search using pgvector
    
    Args:
        query_embedding: The vector to search for
        table_name: Which table to search ('who_guidelines', 'myths', 'educational_content')
        db: Database session
        limit: Number of results to return
    
    Returns:
        List of most similar documents
    """
    from sqlalchemy import text
    
    # Map table name to model
    table_map = {
        'who_guidelines': WHOGuideline,
        'myths': Myth,
        'educational_content': EducationalContent
    }
    
    model = table_map.get(table_name)
    if not model:
        raise ValueError(f"Unknown table: {table_name}")
    
    # Perform cosine similarity search
    results = db.query(model).order_by(
        model.embedding.cosine_distance(query_embedding)
    ).limit(limit).all()
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE SETUP - NURUCARE")
    print("=" * 60)
    
    # Test connection
    if test_connection():
        # Initialize tables
        init_db()
        print("\n✅ Database setup complete!")
    else:
        print("\n❌ Please check your PostgreSQL connection and try again.")