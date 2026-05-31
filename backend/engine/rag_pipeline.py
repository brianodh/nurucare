"""
NuruCare - RAG Pipeline with Gemini Flash
==========================================

This module handles:
1. Converting user questions to embeddings (vector search)
2. Retrieving relevant knowledge from pgvector database
3. Generating intelligent responses using Gemini Flash
4. Calculating confidence scores for recommendations

Author: Brian Odhiambo Ouma
Date: May 31, 2026
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import database modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import get_db
from db.database import WHOGuideline, Myth, EducationalContent
from sqlalchemy import text

# Try to import Gemini
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    print("⚠️ Google GenAI not installed. Run: pip install google-genai")
    GEMINI_AVAILABLE = False


class RAGPipeline:
    """
    Retrieval-Augmented Generation Pipeline for NuruCare
    
    Combines vector search with Gemini Flash to generate
    intelligent, context-aware contraceptive recommendations.
    """
    
    def __init__(self):
        """Initialize the RAG pipeline"""
        print("=" * 60)
        print("🤖 Initializing RAG Pipeline with Gemini Flash")
        print("=" * 60)
        
        # Configure Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_available = GEMINI_AVAILABLE and self.api_key is not None
        
        if self.gemini_available:
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Gemini API configured")
        else:
            print("⚠️ Gemini not available - using fallback mode")
        
        # CORRECT MODEL NAMES (from available models list)
        self.embedding_model = "models/gemini-embedding-001"
        self.generation_model = "models/gemini-2.5-flash"  # or models/gemini-2.0-flash
        
        print(f"   Using embedding model: {self.embedding_model}")
        print(f"   Using generation model: {self.generation_model}")
        print("=" * 60)
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create vector embedding for text using Gemini
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats (embedding vector) or None if failed
        """
        if not self.gemini_available:
            return self._fallback_embedding(text)
        
        try:
            result = self.client.models.embed_content(
                model=self.embedding_model,
                contents=[text[:2000]]
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"   ⚠️ Embedding error: {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str, dimension: int = 768) -> List[float]:
        """Deterministic fallback embedding for testing"""
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        embedding = []
        for i in range(dimension):
            val = (int(hash_hex[i % len(hash_hex)], 16) / 8) - 1
            embedding.append(val)
        return embedding
    
    def retrieve_similar_documents(
        self, 
        query: str, 
        table_name: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve similar documents from vector database
        
        Args:
            query: The search query
            table_name: Which table to search ('who_guidelines', 'myths', 'educational_content')
            limit: Maximum number of results
            
        Returns:
            List of similar documents with content and similarity scores
        """
        # Create embedding for query
        query_embedding = self.create_embedding(query)
        if not query_embedding:
            return []
        
        # Convert embedding to string format for SQL
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
        
        # Map table name to actual table and columns
        table_config = {
            'who_guidelines': {
                'table': 'who_guidelines',
                'content_col': 'content',
                'title_col': 'title',
                'id_col': 'guideline_id'
            },
            'myths': {
                'table': 'myths',
                'content_col': 'myth_statement',
                'title_col': 'truth_statement',
                'id_col': 'myth_id'
            },
            'educational_content': {
                'table': 'educational_content',
                'content_col': 'content',
                'title_col': 'title',
                'id_col': 'content_id'
            }
        }
        
        config = table_config.get(table_name)
        if not config:
            return []
        
        # Query using cosine similarity
        db = next(get_db())
        
        try:
            sql = text(f"""
                SELECT 
                    {config['id_col']} as id,
                    {config['title_col']} as title,
                    {config['content_col']} as content,
                    1 - (embedding <=> CAST(:embedding AS vector)) as similarity
                FROM {config['table']}
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """)
            
            results = db.execute(sql, {
                'embedding': embedding_str,
                'limit': limit
            }).fetchall()
            
            return [
                {
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'similarity': float(row[3]) if row[3] else 0
                }
                for row in results
            ]
        except Exception as e:
            print(f"   ⚠️ Database query error: {e}")
            return []
        finally:
            db.close()
    
    def retrieve_all_relevant(
        self, 
        user_profile: Dict[str, Any],
        allowed_methods: List[str]
    ) -> Dict[str, List[Dict]]:
        """
        Retrieve relevant documents from all tables
        
        Args:
            user_profile: User health data
            allowed_methods: Methods that passed guardrail
            
        Returns:
            Dictionary with retrieved documents by category
        """
        # Create comprehensive query
        query = self._build_retrieval_query(user_profile, allowed_methods)
        
        results = {
            'guidelines': [],
            'myths': [],
            'educational': []
        }
        
        # Retrieve from WHO guidelines
        print("   📚 Retrieving WHO guidelines...")
        results['guidelines'] = self.retrieve_similar_documents(
            query, 'who_guidelines', limit=3
        )
        
        # Retrieve relevant myths
        print("   🧙 Retrieving relevant myths...")
        myth_query = f"contraceptive myths and misconceptions"
        results['myths'] = self.retrieve_similar_documents(
            myth_query, 'myths', limit=2
        )
        
        # Retrieve educational content
        print("   📖 Retrieving educational content...")
        if allowed_methods:
            edu_query = f"contraceptive method benefits and side effects"
            results['educational'] = self.retrieve_similar_documents(
                edu_query, 'educational_content', limit=2
            )
        
        return results
    
    def _build_retrieval_query(self, profile: Dict, allowed_methods: List[str]) -> str:
        """Build a comprehensive query for retrieval"""
        age = profile.get('age', 0)
        fertility = profile.get('fertility_intent', 'unsure')
        
        fertility_text = {
            'want_soon': 'wants to have children soon',
            'want_later': 'wants to have children in the future',
            'no_more': 'does not want more children',
            'unsure': 'is unsure about future children'
        }.get(fertility, 'wants to prevent pregnancy')
        
        query = f"""
        A {age}-year-old person {fertility_text} needs contraceptive recommendations.
        Please provide medical guidelines, effectiveness information, and safety considerations.
        """
        return query.strip()
    
    def calculate_ai_relevance_score(
        self,
        method_id: str,
        method_name: str,
        user_profile: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> float:
        """
        Use Gemini to calculate relevance score (0-10)
        
        Args:
            method_id: The method identifier
            method_name: Display name of the method
            user_profile: User health data
            retrieved_docs: Retrieved relevant documents
            
        Returns:
            Relevance score from 0 to 10
        """
        if not self.gemini_available:
            return 7.0
        
        # Build prompt for Gemini
        age = user_profile.get('age', 0)
        fertility = user_profile.get('fertility_intent', 'unsure')
        
        fertility_text = {
            'want_soon': 'wants children soon',
            'want_later': 'wants children in the future', 
            'no_more': 'does not want more children',
            'unsure': 'unsure about children'
        }.get(fertility, 'wants pregnancy prevention')
        
        prompt = f"""
Rate how well {method_name} matches this user's needs on a scale of 0-10.
User: {age} years old, {fertility_text}
Return ONLY a number between 0 and 10.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            
            # Extract number from response
            text = response.text.strip()
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', text)
            if numbers:
                score = float(numbers[0])
                return min(10, max(0, score))
            else:
                return 7.0
        except Exception as e:
            print(f"   ⚠️ Gemini scoring error: {e}")
            return 7.0
    
    def generate_explanation(
        self,
        method_id: str,
        method_name: str,
        user_profile: Dict[str, Any],
        confidence_score: float,
        retrieved_docs: List[Dict]
    ) -> str:
        """
        Generate personalized explanation using Gemini
        
        Args:
            method_id: The method identifier
            method_name: Display name of the method
            user_profile: User health data
            confidence_score: The calculated confidence score
            retrieved_docs: Retrieved relevant documents
            
        Returns:
            User-friendly explanation
        """
        if not self.gemini_available:
            return self._fallback_explanation(method_id, method_name)
        
        age = user_profile.get('age', 0)
        fertility = user_profile.get('fertility_intent', 'unsure')
        
        fertility_text = {
            'want_soon': 'wants to have children soon',
            'want_later': 'wants to have children in the future',
            'no_more': 'does not want more children',
            'unsure': 'is unsure about future children'
        }.get(fertility, 'wants to prevent pregnancy')
        
        prompt = f"""
Write a short, friendly explanation (2-3 sentences) explaining why {method_name} is a good fit.
User: {age} years old, {fertility_text}
Confidence: {confidence_score}%
Be encouraging and mention reversibility if relevant.
Keep under 150 words.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"   ⚠️ Explanation generation error: {e}")
            return self._fallback_explanation(method_id, method_name)
    
    def _fallback_explanation(self, method_id: str, method_name: str) -> str:
        """Fallback explanations when Gemini is unavailable"""
        explanations = {
            'implants': f"{method_name} is 99% effective and lasts 3-5 years. It requires no daily action and is reversible.",
            'iud_copper': f"{method_name} is 99% effective and lasts up to 10 years. It contains no hormones.",
            'combined_pill': f"{method_name} is 93% effective and can make your periods lighter and more regular.",
            'male_condom': f"{method_name} is 85-98% effective and also protects against STIs.",
            'injectables': f"{method_name} is 94% effective and requires a shot every 3 months.",
        }
        return explanations.get(method_id, f"{method_name} is a good option for you.")
    
    def generate_recommendation_context(
        self,
        user_profile: Dict[str, Any],
        allowed_methods: List[str],
        method_scores: List[Tuple[str, float]]
    ) -> str:
        """
        Generate overall recommendation context using Gemini
        
        Args:
            user_profile: User health data
            allowed_methods: Methods that passed safety check
            method_scores: List of (method_id, confidence_score)
            
        Returns:
            Summary text for the user
        """
        if not self.gemini_available:
            return self._fallback_summary(method_scores)
        
        age = user_profile.get('age', 0)
        fertility = user_profile.get('fertility_intent', 'unsure')
        
        fertility_text = {
            'want_soon': 'wants children soon',
            'want_later': 'wants children in the future',
            'no_more': 'does not want more children',
            'unsure': 'is unsure about future children'
        }.get(fertility, 'wants to prevent pregnancy')
        
        top_methods = method_scores[:3] if method_scores else []
        methods_text = "\n".join([f"- {m[0].replace('_', ' ').title()}: {m[1]}% confidence" for m in top_methods])
        
        prompt = f"""
Write a short, encouraging summary (2-3 sentences) for a contraceptive recommendation.
User: {age} years old, {fertility_text}
Top recommendations:
{methods_text}
Be warm, professional, and mention consulting a healthcare provider.
Keep under 100 words.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"   ⚠️ Summary generation error: {e}")
            return self._fallback_summary(method_scores)
    
    def _fallback_summary(self, method_scores: List[Tuple[str, float]]) -> str:
        """Fallback summary when Gemini unavailable"""
        if method_scores:
            top_method = method_scores[0]
            return f"Based on your health profile, {top_method[0].replace('_', ' ').title()} appears to be a good fit for you with {top_method[1]:.0f}% confidence. Please consult a healthcare provider before making a decision."
        return "Based on your health profile, we've found several contraceptive options for you. Please consult a healthcare provider to discuss which might be best."


# =========================================================
# TESTING THE RAG PIPELINE
# =========================================================

def test_rag_pipeline():
    """Test the RAG pipeline functionality"""
    print("\n" + "=" * 70)
    print("🧪 TESTING RAG PIPELINE")
    print("=" * 70)
    
    # Initialize pipeline
    rag = RAGPipeline()
    
    # Test profile
    test_profile = {
        "age": 28,
        "smoking": False,
        "migraine_type": "none",
        "systolic_bp": 115,
        "diastolic_bp": 75,
        "breastfeeding": False,
        "postpartum_weeks": 100,
        "fertility_intent": "want_later",
        "cycle_regularity": "regular"
    }
    
    allowed_methods = [
        "implants", "iud_copper", "combined_pill", 
        "male_condom", "injectables"
    ]
    
    print("\n📋 Test Profile:")
    for key, value in test_profile.items():
        print(f"   {key}: {value}")
    
    # Test retrieval
    print("\n📚 Testing Knowledge Retrieval...")
    results = rag.retrieve_all_relevant(test_profile, allowed_methods)
    
    print(f"\n   Retrieved {len(results['guidelines'])} WHO guidelines")
    for doc in results['guidelines'][:2]:
        print(f"      - {doc.get('title', 'No title')[:50]}... (similarity: {doc.get('similarity', 0):.2f})")
    
    print(f"\n   Retrieved {len(results['myths'])} myths")
    for doc in results['myths']:
        print(f"      - {doc.get('title', 'No title')[:50]}...")
    
    # Test AI relevance scoring
    print("\n🎯 Testing AI Relevance Scoring...")
    score = rag.calculate_ai_relevance_score(
        "implants", "Implant", test_profile, results['guidelines']
    )
    print(f"   Implant relevance score: {score}/10")
    
    # Test explanation generation
    print("\n💬 Testing Explanation Generation...")
    explanation = rag.generate_explanation(
        "implants", "Implant", test_profile, 85, results['guidelines']
    )
    print(f"   Explanation: {explanation[:150]}...")
    
    # Test summary generation
    print("\n📝 Testing Summary Generation...")
    method_scores = [("implants", 92), ("iud_copper", 88), ("combined_pill", 85)]
    summary = rag.generate_recommendation_context(test_profile, allowed_methods, method_scores)
    print(f"   Summary: {summary}")
    
    print("\n" + "=" * 70)
    print("✅ RAG Pipeline Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    test_rag_pipeline()