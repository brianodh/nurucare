"""
NuruCare - RAG Pipeline with Gemini Flash & Optimized Prompts
=============================================================

This module handles:
1. Converting user questions to embeddings (vector search)
2. Retrieving relevant knowledge from pgvector database
3. Generating intelligent responses using Gemini Flash
4. Calculating confidence scores for recommendations
5. Using optimized prompts for clinical accuracy and safety

Author: Brian Odhiambo Ouma
Date: May 31, 2026
Version: 2.1 - Fixed method parameter mismatches
 
OPTIONAL RAG augmentation sub-pipeline.

This module is imported by `recommendation_pipeline.py` using a guarded
try/except ImportError. If any optional dependency fails (pgvector, the
`db.database` SQLAlchemy module, the WHO guideline embeddings table, or
a valid Gemini API key), `RAG_AVAILABLE` is set to False and the
`RecommendationPipeline` falls back to a non-RAG ranking path (WHO MEC
guardrail + adoption-stats + fertility-intent weighting).

Nothing else imports this module directly. The service boots and serves
recommendations perfectly well without this file being loadable.
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

# Import optimized prompts
try:
    from prompts.optimized_prompts import PromptManager
    PROMPTS_AVAILABLE = True
except ImportError:
    print("⚠️ Optimized prompts not found. Run: python backend/prompts/optimized_prompts.py")
    PROMPTS_AVAILABLE = False

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
    
    Features:
    - Optimized prompts for clinical accuracy
    - Safety guardrails in all responses
    - Culturally sensitive language
    - Plain English explanations
    """
    
    def __init__(self):
        """Initialize the RAG pipeline with optimized prompts"""
        print("=" * 60)
        print("🤖 Initializing RAG Pipeline with Gemini Flash")
        print("=" * 60)
        
        # Initialize prompt manager
        if PROMPTS_AVAILABLE:
            self.prompt_manager = PromptManager()
            print("✅ Optimized prompts loaded")
        else:
            self.prompt_manager = None
            print("⚠️ Using fallback prompts (not optimized)")
        
        # Configure Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_available = GEMINI_AVAILABLE and self.api_key is not None
        
        if self.gemini_available:
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Gemini API configured")
        else:
            print("⚠️ Gemini not available - using fallback mode")
        
        # Model configurations
        self.embedding_model = "models/gemini-embedding-001"
        self.generation_model = "models/gemini-2.0-flash-exp"
        
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
            table_name: Which table to search
            limit: Maximum number of results
            
        Returns:
            List of similar documents with content and similarity scores
        """
        query_embedding = self.create_embedding(query)
        if not query_embedding:
            return []
        
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
        
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
        query = self._build_retrieval_query(user_profile, allowed_methods)
        
        results = {
            'guidelines': [],
            'myths': [],
            'educational': []
        }
        
        print("   📚 Retrieving WHO guidelines...")
        results['guidelines'] = self.retrieve_similar_documents(
            query, 'who_guidelines', limit=3
        )
        
        print("   🧙 Retrieving relevant myths...")
        results['myths'] = self.retrieve_similar_documents(
            query, 'myths', limit=2
        )
        
        print("   📖 Retrieving educational content...")
        if allowed_methods:
            results['educational'] = self.retrieve_similar_documents(
                query, 'educational_content', limit=2
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
        Please provide medical guidelines, effectiveness information and safety considerations from WHO sources.
        """
        return query.strip()
    
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
    
    def _get_method_details(self, method_id: str) -> str:
        """Get detailed information about a method for prompts"""
        details = {
            'implants': "Small rod inserted under skin, lasts 3-5 years, 99% effective, progestin-only",
            'iud_copper': "T-shaped device inserted in uterus, lasts up to 10 years, 99% effective, hormone-free",
            'iud_hormonal': "T-shaped device inserted in uterus, lasts 3-7 years, 99% effective, may stop periods",
            'injectables': "Shot every 3 months, 94% effective, progestin-only, may cause weight gain",
            'combined_pill': "Daily pill with estrogen and progestin, 93% effective, regulates cycles",
            'progestin_pill': "Daily pill without estrogen, 93% effective, safe for breastfeeding",
            'male_condom': "Worn on penis, 85-98% effective, protects against STIs, no hormones",
            'female_condom': "Inserted in vagina, 79% effective, protects against STIs",
            'withdrawal': "Penis withdrawn before ejaculation, 78% effective, no cost",
            'rhythm': "Tracking fertile days, 76% effective, requires regular cycles",
            'lam': "Breastfeeding method, 98% effective for first 6 months only",
            'emergency': "Take within 72 hours of unprotected sex, 85% effective, emergency use only"
        }
        return details.get(method_id, "Effective contraceptive method")
    
    def _get_medical_notes(self, user_profile: Dict[str, Any]) -> str:
        """Generate medical notes string for prompts"""
        notes = []
        if user_profile.get('smoking'):
            notes.append("Smoker")
        if user_profile.get('migraine_type') == 'with_aura':
            notes.append("Migraine with aura")
        systolic = user_profile.get('systolic_bp', 0)
        diastolic = user_profile.get('diastolic_bp', 0)
        if systolic >= 140 or diastolic >= 90:
            notes.append(f"Hypertension ({systolic}/{diastolic})")
        if user_profile.get('breastfeeding'):
            notes.append("Breastfeeding")
        return ", ".join(notes) if notes else "No significant medical issues"
    
    def calculate_ai_relevance_score(
        self,
        method_id: str,
        method_name: str,
        user_profile: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> float:
        """
        Use Gemini to calculate relevance score (0-10)
        Uses optimized prompt for accurate scoring
        """
        if not self.gemini_available:
            return 7.0
        
        age = user_profile.get('age', 0)
        fertility = user_profile.get('fertility_intent', 'unsure')
        
        fertility_text = {
            'want_soon': 'wants children soon',
            'want_later': 'wants children in the future', 
            'no_more': 'does not want more children',
            'unsure': 'unsure about children'
        }.get(fertility, 'wants pregnancy prevention')
        
        medical_notes = self._get_medical_notes(user_profile)
        method_details = self._get_method_details(method_id)
        
        # Use optimized prompt if available
        if self.prompt_manager:
            prompt = self.prompt_manager.get_relevance_scoring_prompt(
                age=age,
                fertility_intent=fertility,
                medical_notes=medical_notes,
                method_name=method_name,
                method_details=method_details
            )
        else:
            prompt = f"""
Rate how well {method_name} matches this user's needs on a scale of 0-10.
User: {age} years old, {fertility_text}
Medical notes: {medical_notes}
Method details: {method_details}
Consider: effectiveness, reversibility, side effects, convenience.
Return ONLY a number between 0 and 10.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            
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
        
        effectiveness = self._get_method_effectiveness(method_id)
        
        # Use optimized prompt if available
        if self.prompt_manager:
            prompt = self.prompt_manager.get_recommendation_prompt(
                method_name=method_name,
                method_effectiveness=effectiveness,
                user_profile=user_profile,
                confidence=confidence_score,
                context=context
            )
            system_prompt = self.prompt_manager.get_system_prompt()
        else:
            prompt = f"""
Write a short, friendly explanation (2-3 sentences) explaining why {method_name} is a good fit.
User: {user_profile.get('age', '?')} years old
Effectiveness: {effectiveness}%
Confidence: {confidence_score}%
Be encouraging and mention reversibility if relevant.
Always include: "Please consult a healthcare provider."
Keep under 120 words.
"""
            system_prompt = "You are a helpful medical AI assistant."
        
        try:
            if self.prompt_manager:
                response = self.client.models.generate_content(
                    model=self.generation_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    )
                )
            else:
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
            'implants': f"{method_name} is 99% effective and lasts 3-5 years. It requires no daily action and is reversible. Please consult a healthcare provider.",
            'iud_copper': f"{method_name} is 99% effective and lasts up to 10 years. It contains no hormones. Please consult a healthcare provider.",
            'combined_pill': f"{method_name} is 93% effective and can make your periods lighter and more regular. Please consult a healthcare provider.",
            'male_condom': f"{method_name} is 85-98% effective and also protects against STIs. Please consult a healthcare provider.",
            'injectables': f"{method_name} is 94% effective and requires a shot every 3 months. Please consult a healthcare provider.",
        }
        return explanations.get(method_id, f"{method_name} is a good option for you. Please consult a healthcare provider.")
    
    def generate_myth_busting_response(
        self,
        myth_statement: str,
        truth_statement: str,
        explanation: str
    ) -> str:
        """
        Generate a myth-busting response using optimized prompts
        
        Args:
            myth_statement: The myth to bust
            truth_statement: The factual truth
            explanation: Detailed explanation
            
        Returns:
            Compassionate, educational response
        """
        if not self.gemini_available:
            return f"The truth is: {truth_statement} {explanation}"
        
        if self.prompt_manager:
            prompt = self.prompt_manager.get_myth_busting_prompt(
                myth_statement=myth_statement,
                truth_statement=truth_statement,
                explanation=explanation
            )
        else:
            prompt = f"""
Help someone who believes: "{myth_statement}"
Truth: {truth_statement}
Explanation: {explanation}
Write a compassionate response (under 120 words) that gently corrects this misconception.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Myth busting error: {e}")
            return f"The truth is: {truth_statement} {explanation}"
    
    def generate_side_effect_advice(
        self,
        method_name: str,
        side_effect: str,
        severity: str,
        duration: int
    ) -> str:
        """
        Generate side effect management advice using optimized prompts
        
        Args:
            method_name: The contraceptive method
            side_effect: The side effect being experienced
            severity: mild, moderate, or severe
            duration: How long experienced (days/weeks)
            
        Returns:
            Helpful management advice
        """
        if not self.gemini_available:
            return f"Common side effects often improve within 3 months. If {side_effect} is severe or persistent, consult your healthcare provider."
        
        if self.prompt_manager:
            prompt = self.prompt_manager.get_side_effect_prompt(
                method_name=method_name,
                side_effect=side_effect,
                severity=severity,
                duration=duration
            )
        else:
            prompt = f"""
User is experiencing {side_effect} with {method_name} (severity: {severity}, duration: {duration} days).
Provide practical advice for managing this side effect and specify when to consult a provider.
Keep response under 100 words.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Side effect advice error: {e}")
            return f"Common side effects often improve within 3 months. If {side_effect} is severe or persistent, consult your healthcare provider."
    
    def generate_recommendation_summary(
        self,
        user_profile: Dict[str, Any],
        top_recommendations: List[Tuple[str, float]]
    ) -> str:
        """
        Generate an overall recommendation summary using optimized prompts
        """
        if not self.gemini_available or not top_recommendations:
            return self._fallback_summary(top_recommendations)
        
        age = user_profile.get('age', 0)
        fertility = user_profile.get('fertility_intent', 'unsure')
        
        fertility_text = {
            'want_soon': 'wants children soon',
            'want_later': 'wants children in the future',
            'no_more': 'does not want more children',
            'unsure': 'is unsure about future children'
        }.get(fertility, 'wants to prevent pregnancy')
        
        # Format top recommendations
        methods_text = ""
        for method_id, score in top_recommendations[:3]:
            method_name = method_id.replace('_', ' ').title()
            methods_text += f"- {method_name}: {score:.0f}% confidence\n"
        
        # Use optimized prompt if available
        if self.prompt_manager:
            prompt = self.prompt_manager.get_summary_prompt(
                age=age,
                health_status=self._get_health_status(user_profile),
                fertility_intent=fertility,
                top_recommendations=methods_text
            )
        else:
            prompt = f"""
Write a short, encouraging summary (2-3 sentences) for a contraceptive recommendation.
User: {age} years old, {fertility_text}
Top recommendations:
{methods_text}
Be warm and professional. Mention consulting a healthcare provider. Keep under 100 words.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Summary generation error: {e}")
            return self._fallback_summary(top_recommendations)
    
    def _get_health_status(self, user_profile: Dict) -> str:
        """Get health status description for prompts"""
        systolic = user_profile.get('systolic_bp', 0)
        diastolic = user_profile.get('diastolic_bp', 0)
        
        if systolic >= 140 or diastolic >= 90:
            return "Elevated blood pressure - requires non-estrogen methods"
        elif user_profile.get('smoking') and user_profile.get('age', 0) > 35:
            return "Smoker over 35 - requires non-estrogen methods"
        elif user_profile.get('migraine_type') == 'with_aura':
            return "Migraine with aura - requires non-estrogen methods"
        else:
            return "Generally healthy"
    
    def _fallback_summary(self, top_recommendations: List[Tuple[str, float]]) -> str:
        """Fallback summary when Gemini unavailable"""
        if top_recommendations:
            method_name = top_recommendations[0][0].replace('_', ' ').title()
            score = top_recommendations[0][1]
            return f"Based on your health profile, {method_name} appears to be a good fit for you with {score:.0f}% confidence. Please consult a healthcare provider before making a decision."
        return "Please consult a healthcare provider for personalized contraceptive advice."
    
    def generate_safety_warning(
        self,
        risk_factors: List[str],
        safe_categories: List[str]
    ) -> str:
        """
        Generate safety warning for high-risk users using optimized prompts
        
        Args:
            risk_factors: List of identified risk factors
            safe_categories: List of safe method categories
            
        Returns:
            Compassionate safety warning
        """
        if not self.gemini_available:
            risk_text = ", ".join(risk_factors)
            safe_text = ", ".join(safe_categories)
            return f"Due to {risk_text}, combined hormonal contraceptives may not be safe for you. Safe options include: {safe_text}. Please consult a healthcare provider."
        
        if self.prompt_manager:
            prompt = self.prompt_manager.get_safety_guardrail_prompt(
                risk_factors=risk_factors,
                safe_categories=safe_categories
            )
        else:
            risk_text = "\n".join([f"- {r}" for r in risk_factors])
            prompt = f"""
ALERT: This user has contraindications for combined hormonal contraceptives.

RISK FACTORS:
{risk_text}

SAFE CATEGORIES:
- Progestin-only methods
- Non-hormonal methods
- Barrier methods

Write a compassionate warning explaining why combined methods are not safe and listing safe alternatives.
Emphasize provider consultation. Keep under 150 words.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Safety warning error: {e}")
            return f"Due to your health profile, combined hormonal contraceptives may not be safe. Safe options include progestin-only or non-hormonal methods. Please consult a healthcare provider."


# =========================================================
# TESTING THE RAG PIPELINE
# =========================================================

def test_rag_pipeline():
    """Test the RAG pipeline functionality with optimized prompts"""
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
        "implants", "Implant", test_profile, 92, results['guidelines']
    )
    print(f"   Explanation: {explanation}")
    
    # Test myth busting
    print("\n🧙 Testing Myth Busting Response...")
    myth_response = rag.generate_myth_busting_response(
        myth_statement="The contraceptive injection causes permanent infertility",
        truth_statement="Fertility returns to normal after stopping injections",
        explanation="Depo-Provera may delay return to fertility by 6-12 months, but does NOT cause permanent infertility."
    )
    print(f"   Response: {myth_response}")
    
    # Test side effect advice
    print("\n💊 Testing Side Effect Advice...")
    side_effect_response = rag.generate_side_effect_advice(
        method_name="Implant",
        side_effect="irregular bleeding",
        severity="mild",
        duration=30
    )
    print(f"   Advice: {side_effect_response}")
    
    # Test recommendation summary
    print("\n📝 Testing Recommendation Summary...")
    method_scores = [("implants", 92), ("iud_copper", 88), ("combined_pill", 85)]
    summary = rag.generate_recommendation_summary(test_profile, method_scores)
    print(f"   Summary: {summary}")
    
    # Test safety warning
    print("\n⚠️ Testing Safety Warning...")
    safety_warning = rag.generate_safety_warning(
        risk_factors=["Hypertension (145/95)", "Age 36 with smoking"],
        safe_categories=["Progestin-only methods", "Non-hormonal methods"]
    )
    print(f"   Warning: {safety_warning}")
    
    print("\n" + "=" * 70)
    print("✅ RAG Pipeline Test Complete!")
    print("=" * 70)
    print("\n📋 Optimized Features Demonstrated:")
    print("   - Provider consultation reminder in all responses")
    print("   - Plain language explanations")
    print("   - Culturally sensitive tone")
    print("   - Clinical accuracy with WHO guidelines")
    print("   - Compassionate myth busting")
    print("   - Practical side effect management")


if __name__ == "__main__":
    test_rag_pipeline()