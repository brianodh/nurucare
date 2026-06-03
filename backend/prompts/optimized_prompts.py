"""
NuruCare - RAG Pipeline with Gemini Flash
==========================================

This module handles:
1. Converting user questions to embeddings (vector search)
2. Retrieving relevant knowledge from pgvector database
3. Generating intelligent responses using Gemini Flash
4. Calculating confidence scores for recommendations

Version: 2.1
Last Updated: May 31, 2026
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import database modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import get_db
from db.database import WHOGuideline, Myth, EducationalContent
from sqlalchemy import text

# Import prompt manager
from prompts.optimized_prompts import PromptManager

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
        
        # Initialize prompt manager
        self.prompt_manager = PromptManager()
        print("✅ Optimized prompts loaded")
        
        # Configure Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_available = GEMINI_AVAILABLE and self.api_key is not None
        
        if self.gemini_available:
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Gemini API configured")
        else:
            print("⚠️ Gemini Flash not available - using fallback mode")
        
        # Model configurations
        self.embedding_model = "models/text-embedding-004"
        self.generation_model = "models/gemini-2.0-flash-exp"
        
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
                contents=[text[:2000]]  # Limit text length
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
        myth_query = f"contraceptive myths and misconceptions about {allowed_methods[0] if allowed_methods else 'family planning'}"
        results['myths'] = self.retrieve_similar_documents(
            myth_query, 'myths', limit=2
        )
        
        # Retrieve educational content
        print("   📖 Retrieving educational content...")
        if allowed_methods:
            edu_query = f"benefits and side effects of {allowed_methods[0]}"
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
        Safe methods include: {', '.join(allowed_methods[:5]) if allowed_methods else 'various methods'}.
        Please provide medical guidelines, effectiveness information, and safety considerations.
        """
        return query.strip()
    
    def _get_method_details(self, method_id: str) -> str:
        """Get details about a contraceptive method"""
        method_details = {
            'implants': "Small rod inserted under skin, lasts 3-5 years, 99% effective, reversible.",
            'iud_copper': "T-shaped device inserted into uterus, lasts up to 10 years, 99% effective, hormone-free.",
            'iud_hormonal': "T-shaped device with hormones, lasts 3-7 years, 99% effective, lighter periods.",
            'injectables': "Shot every 3 months, 94% effective, private, no daily action.",
            'combined_pill': "Daily pill with estrogen and progestin, 93% effective, lighter periods.",
            'progestin_pill': "Daily pill without estrogen, 93% effective, safe for breastfeeding.",
            'male_condom': "Barrier method, 85-98% effective, protects against STIs.",
            'female_condom': "Barrier method inserted before sex, protects against STIs.",
            'withdrawal': "Withdraw before ejaculation, 78% effective, requires no supplies.",
            'rhythm': "Track fertile days, 76% effective, requires cycle tracking.",
            'lam': "Breastfeeding method, 98% effective for first 6 months postpartum.",
            'emergency': "Take within 72 hours of unprotected sex, 85% effective.",
            'sterilization_female': "Permanent surgical procedure, 99% effective.",
            'sterilization_male': "Permanent surgical procedure for men, 99% effective."
        }
        return method_details.get(method_id, "Effective contraceptive method.")
    
    def _get_method_effectiveness(self, method_id: str) -> int:
        """Get effectiveness percentage for a method"""
        effectiveness = {
            'implants': 99,
            'iud_copper': 99,
            'iud_hormonal': 99,
            'sterilization_female': 99,
            'sterilization_male': 99,
            'injectables': 94,
            'combined_pill': 93,
            'progestin_pill': 93,
            'male_condom': 85,
            'female_condom': 79,
            'withdrawal': 78,
            'rhythm': 76,
            'emergency': 85,
            'lam': 98
        }
        return effectiveness.get(method_id, 90)
    
    def calculate_ai_relevance_score(
        self,
        method_id: str,
        method_name: str,
        user_profile: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> float:
        """
        Use Gemini Flash to calculate relevance score (0-10)
        
        Args:
            method_id: The method identifier
            method_name: Display name of the method
            user_profile: User health data
            retrieved_docs: Retrieved relevant documents
            
        Returns:
            Relevance score from 0 to 10
        """
        if not self.gemini_available:
            return 7.0  # Default moderate score
        
        age = user_profile.get('age', 0)
        fertility_intent = user_profile.get('fertility_intent', 'unsure')
        
        # Determine medical notes
        medical_notes = []
        if user_profile.get('smoking'):
            medical_notes.append("Smoker")
        if user_profile.get('migraine_type') == 'with_aura':
            medical_notes.append("Migraine with aura")
        systolic = user_profile.get('systolic_bp', 0)
        diastolic = user_profile.get('diastolic_bp', 0)
        if systolic >= 140 or diastolic >= 90:
            medical_notes.append(f"Hypertension ({systolic}/{diastolic})")
        if user_profile.get('breastfeeding'):
            medical_notes.append("Breastfeeding")
        
        medical_notes_text = ", ".join(medical_notes) if medical_notes else "No significant medical issues"
        
        # Use optimized prompt (no method_details parameter)
        prompt = self.prompt_manager.get_relevance_scoring_prompt(
            age=age,
            fertility_intent=fertility_intent,
            medical_notes=medical_notes_text,
            method_name=method_name
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            
            # Extract number from response
            text = response.text.strip()
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
        Generate personalized explanation using optimized prompts
        """
        if not self.gemini_available:
            return self._fallback_explanation(method_id, method_name)
        
        # Build context from retrieved documents
        context = ""
        for doc in retrieved_docs[:2]:
            context += f"{doc.get('content', '')[:300]}...\n"
        
        # Use optimized prompt
        prompt = self.prompt_manager.get_recommendation_prompt(
            method_name=method_name,
            user_profile=user_profile,
            confidence=confidence_score,
            context=context
        )
        
        # Get system prompt
        system_prompt = self.prompt_manager.get_system_prompt()
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"   ⚠️ Explanation generation error: {e}")
            return self._fallback_explanation(method_id, method_name)
    
    def _fallback_explanation(self, method_id: str, method_name: str) -> str:
        """Fallback explanations when Gemini is unavailable"""
        explanations = {
            'implants': f"{method_name} is 99% effective and lasts 3-5 years. It requires no daily action and is reversible. Please consult a healthcare provider before making a decision.",
            'iud_copper': f"{method_name} is 99% effective and lasts up to 10 years. It contains no hormones. Please consult a healthcare provider before making a decision.",
            'combined_pill': f"{method_name} is 93% effective and can make your periods lighter and more regular. Please consult a healthcare provider before making a decision.",
            'male_condom': f"{method_name} is 85-98% effective and also protects against STIs. Please consult a healthcare provider for proper use instructions.",
            'injectables': f"{method_name} is 94% effective and requires a shot every 3 months. Please consult a healthcare provider before making a decision.",
        }
        return explanations.get(method_id, f"{method_name} is a good option for you. Please consult a healthcare provider before making a decision.")
    
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
        
        # Build health status
        health_issues = []
        if user_profile.get('smoking'):
            health_issues.append("smoking")
        if user_profile.get('migraine_type') == 'with_aura':
            health_issues.append("migraine with aura")
        systolic = user_profile.get('systolic_bp', 0)
        diastolic = user_profile.get('diastolic_bp', 0)
        if systolic >= 140 or diastolic >= 90:
            health_issues.append("hypertension")
        
        health_status = "No significant health issues" if not health_issues else f"Considerations: {', '.join(health_issues)}"
        
        # Format top recommendations
        top_methods = method_scores[:3]
        methods_text = "\n".join([f"- {self._get_method_name(m[0])}: {m[1]:.0f}% confidence" for m in top_methods])
        
        # Use optimized prompt
        prompt = self.prompt_manager.get_summary_prompt(
            age=age,
            health_status=health_status,
            fertility_intent=fertility,
            top_recommendations=methods_text
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"   ⚠️ Summary generation error: {e}")
            return self._fallback_summary(method_scores)
    
    def _get_method_name(self, method_id: str) -> str:
        """Get display name for a method"""
        method_names = {
            'implants': 'Implant',
            'iud_copper': 'Copper IUD',
            'iud_hormonal': 'Hormonal IUD',
            'injectables': 'Injectable (Depo-Provera)',
            'combined_pill': 'Combined Pill',
            'progestin_pill': 'Mini-Pill',
            'male_condom': 'Male Condom',
            'female_condom': 'Female Condom',
            'withdrawal': 'Withdrawal',
            'rhythm': 'Rhythm Method',
            'lam': 'LAM (Breastfeeding)',
            'emergency': 'Emergency Contraception',
            'sterilization_female': 'Tubal Ligation',
            'sterilization_male': 'Vasectomy'
        }
        return method_names.get(method_id, method_id.replace('_', ' ').title())
    
    def _fallback_summary(self, method_scores: List[Tuple[str, float]]) -> str:
        """Fallback summary when Gemini unavailable"""
        if not method_scores:
            return "Based on your health profile, please consult a healthcare provider for personalized contraceptive advice."
        top_method = method_scores[0]
        method_name = self._get_method_name(top_method[0])
        return f"Based on your health profile, {method_name} appears to be a good fit for you with {top_method[1]:.0f}% confidence. Please consult a healthcare provider before making a decision."


# =========================================================
# TESTING THE RAG PIPELINE
# =========================================================

def test_rag_pipeline():
    """Test the RAG pipeline functionality"""
    print("\n" + "=" * 70)
    print("🧪 TESTING RAG PIPELINE WITH OPTIMIZED PROMPTS")
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
        print(f"      - {doc['title'][:40]}... (similarity: {doc['similarity']:.2f})")
    
    print(f"\n   Retrieved {len(results['myths'])} myths")
    for doc in results['myths']:
        print(f"      - {doc['title'][:40]}...")
    
    # Test AI relevance scoring
    print("\n🎯 Testing AI Relevance Scoring...")
    score = rag.calculate_ai_relevance_score(
        "implants", "Implant", test_profile, results['guidelines']
    )
    print(f"   Implant relevance score: {score}/10")
    
    # Test explanation generation
    print("\n💬 Testing Explanation Generation...")
    explanation = rag.generate_explanation(
        "implants", "Implant", test_profile, 92, results['guidelines']
    )
    print(f"   Explanation: {explanation[:150]}...")
    
    # Test recommendation context
    print("\n📝 Testing Recommendation Summary...")
    method_scores = [("implants", 92), ("iud_copper", 88), ("combined_pill", 85)]
    summary = rag.generate_recommendation_context(test_profile, allowed_methods, method_scores)
    print(f"   Summary: {summary[:200]}...")
    
    print("\n" + "=" * 70)
    print("✅ RAG Pipeline Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    test_rag_pipeline()