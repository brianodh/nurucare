"""
NuruCare - Complete Recommendation Pipeline
===========================================

This module combines the WHO MEC Guardrail Engine with the RAG Pipeline
to produce safe, personalized contraceptive recommendations.

Pipeline Flow:
1. Guardrail evaluates safety -> restricts unsafe methods
2. RAG retrieves knowledge and ranks allowed methods
3. Pipeline combines results into final response

Author: Brian Odhiambo Ouma
Date: May 31, 2026
"""

# =========================================================
# FIX: Add project root to Python path
# =========================================================
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Also add backend directory
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

print(f"📁 Project root: {PROJECT_ROOT}")
print(f"📁 Backend directory: {backend_dir}")

# =========================================================
# Continue with normal imports
# =========================================================

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Now import from engine
from engine.guardrail import WHOMECGuardrail

# Import RAG pipeline
try:
    from engine.rag_pipeline import RAGPipeline
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ RAG pipeline not available: {e}")
    RAG_AVAILABLE = False

class RecommendationPipeline:
    """
    Complete recommendation pipeline combining Guardrail + RAG
    
    This orchestrates the entire recommendation flow:
    1. Safety check (WHO MEC)
    2. Knowledge retrieval (RAG)
    3. Ranking and explanation generation
    """
    
    def __init__(self):
        """Initialize the pipeline with all components"""
        print("=" * 60)
        print("🚀 Initializing NuruCare Recommendation Pipeline")
        print("=" * 60)
        
        # Initialize guardrail engine
        self.guardrail = WHOMECGuardrail()
        print("✅ Guardrail engine loaded")
        
        # Initialize RAG pipeline (if available)
        if RAG_AVAILABLE:
            try:
                self.rag = RAGPipeline()
                print("✅ RAG pipeline loaded")
            except Exception as e:
                print(f"⚠️ RAG pipeline failed to load: {e}")
                self.rag = None
        else:
            self.rag = None
            print("⚠️ RAG pipeline not available - using fallback ranking")
        
        # Method ranking weights (from Client Service Statistics dataset)
        self.method_weights = self._load_method_weights()
        print(f"✅ Loaded method weights for {len(self.method_weights)} methods")
        
        print("=" * 60)
    
    def _load_method_weights(self) -> Dict[str, float]:
        """
        Load method ranking weights based on real adoption data
        
        From Client Service Statistics dataset (216,539 records):
        - Condoms: 40.3% of adoptions
        - Pills: 22.2%
        - Implants: 15.7%
        - Injectables: 15.2%
        - IUCD: 2.1%
        """
        return {
            'male_condom': 0.403,
            'combined_pill': 0.222,
            'implants': 0.157,
            'injectables': 0.152,
            'iud_copper': 0.021,
            'iud_hormonal': 0.018,
            'progestin_pill': 0.012,
            'female_condom': 0.008,
            'emergency': 0.005,
            'withdrawal': 0.002,
            'rhythm': 0.001,
            'lam': 0.001,
            'sterilization_female': 0.001,
            'sterilization_male': 0.0005,
            'combined_patch': 0.0005,
            'combined_ring': 0.0005,
        }
    
    def _get_method_name(self, method_id: str) -> str:
        """Get display name for a method"""
        method_names = {
            'implants': 'Implant',
            'iud_copper': 'Copper IUD',
            'iud_hormonal': 'Hormonal IUD',
            'injectables': 'Injectable (Depo-Provera)',
            'combined_pill': 'Combined Oral Contraceptive Pill',
            'progestin_pill': 'Progestin-Only Pill (Mini-Pill)',
            'male_condom': 'Male Condom',
            'female_condom': 'Female Condom',
            'withdrawal': 'Withdrawal Method',
            'rhythm': 'Rhythm Method',
            'lam': 'Lactational Amenorrhea Method (LAM)',
            'emergency': 'Emergency Contraception (P2)',
            'sterilization_female': 'Tubal Ligation',
            'sterilization_male': 'Vasectomy',
            'combined_patch': 'Contraceptive Patch',
            'combined_ring': 'Vaginal Ring',
            'combined_oral_contraceptives': 'Combined Oral Contraceptive'
        }
        return method_names.get(method_id, method_id.replace('_', ' ').title())
    
    def _match_fertility_intent(self, method_id: str, intent: str) -> float:
        """
        Match method to fertility intent
        1.0 = perfect match, 0.5 = acceptable, 0.0 = poor match
        """
        # Methods that preserve fertility (reversible)
        reversible_methods = [
            'male_condom', 'female_condom', 'combined_pill', 'progestin_pill',
            'injectables', 'implants', 'iud_copper', 'iud_hormonal',
            'withdrawal', 'rhythm', 'lam', 'emergency', 'combined_patch', 'combined_ring'
        ]
        
        # Permanent methods (sterilization)
        permanent_methods = ['sterilization_female', 'sterilization_male']
        
        if intent == 'want_soon' or intent == 'want_later':
            # User wants children in future - recommend reversible methods
            if method_id in reversible_methods:
                return 1.0
            elif method_id in permanent_methods:
                return 0.0
            else:
                return 0.5
                
        elif intent == 'no_more':
            # User doesn't want more children - permanent methods are good
            if method_id in permanent_methods:
                return 1.0
            elif method_id in reversible_methods:
                return 0.7
            else:
                return 0.5
                
        else:  # 'unsure' or default
            return 0.5
    
    def _calculate_confidence_score(
        self, 
        method_id: str, 
        user_profile: Dict[str, Any],
        retrieved_context: Optional[List[Dict]] = None
    ) -> float:
        """
        Calculate confidence score (0-100) for a method
        
        Factors:
        - Medical fit (from guardrail - no restrictions = 40 points)
        - Popularity weight (from real adoption data = 30 points)
        - User preference match (fertility intent = 20 points)
        - AI relevance (Gemini evaluation = 10 points)
        """
        score = 0.0
        
        # Factor 1: Medical fit (40 points)
        # Methods allowed by guardrail get full points
        score += 40
        print(f"      Medical fit: +40")
        
        # Factor 2: Popularity weight (30 points)
        popularity = self.method_weights.get(method_id, 0.01)
        popularity_score = popularity * 30
        score += popularity_score
        print(f"      Popularity: +{popularity_score:.1f} (weight: {popularity:.3f})")
        
        # Factor 3: User preference match (20 points)
        fertility_intent = user_profile.get('fertility_intent', 'unsure')
        match_score = self._match_fertility_intent(method_id, fertility_intent) * 20
        score += match_score
        print(f"      Preference match: +{match_score:.1f}")
        
        # Factor 4: AI Relevance (10 points) - if RAG available
        if self.rag and retrieved_context:
            try:
                ai_score = self.rag.calculate_ai_relevance_score(
                    method_id,
                    self._get_method_name(method_id),
                    user_profile,
                    retrieved_context
                )
                score += ai_score
                print(f"      AI relevance: +{ai_score:.1f}")
            except Exception as e:
                print(f"      AI relevance: +0 (error: {e})")
        else:
            print(f"      AI relevance: +0 (RAG not available)")
        
        # Normalize to 0-100
        final_score = min(100, max(0, score))
        print(f"      TOTAL: {final_score:.1f}%")
        
        return final_score
    
    def _generate_explanation(
        self, 
        method_id: str, 
        method_name: str,
        user_profile: Dict[str, Any],
        confidence_score: float,
        retrieved_context: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate user-friendly explanation for recommendation
        """
        # Try RAG-generated explanation first
        if self.rag and retrieved_context:
            try:
                rag_explanation = self.rag.generate_explanation(
                    method_id, method_name, user_profile, confidence_score, retrieved_context
                )
                if rag_explanation and len(rag_explanation) > 20:
                    return rag_explanation
            except Exception as e:
                print(f"      RAG explanation failed: {e}")
        
        # Fallback explanations
        age = user_profile.get('age', 0)
        fertility_intent = user_profile.get('fertility_intent', 'unsure')
        
        explanations = {
            'implants': f"The implant is 99% effective and lasts 3-5 years. It's a great choice because it requires no daily action and is reversible.",
            'iud_copper': f"The copper IUD is 99% effective and lasts up to 10 years. It contains no hormones, making it ideal if you prefer non-hormonal options.",
            'iud_hormonal': f"The hormonal IUD is 99% effective and lasts 3-7 years. It often makes periods lighter or stops them completely.",
            'injectables': f"The injection (Depo-Provera) is 94% effective and requires a shot every 3 months. It's private and requires no daily action.",
            'combined_pill': f"The combined pill is 93% effective when taken daily. It can make your periods lighter and more regular.",
            'progestin_pill': f"The mini-pill is 93% effective when taken daily at the same time. It's safe if you can't take estrogen.",
            'male_condom': f"Condoms are 85% effective with typical use (98% with perfect use). They also protect against STIs including HIV.",
            'female_condom': f"Female condoms are 79% effective and can be inserted before sex. They also protect against STIs.",
            'withdrawal': f"Withdrawal is 78% effective when done correctly every time. It requires no supplies but has higher failure rates.",
            'rhythm': f"The rhythm method is 76% effective when you track your cycle accurately. It works best with regular cycles.",
            'lam': f"LAM is 98% effective when you're exclusively breastfeeding and haven't had a period. It's a natural option for new mothers.",
            'emergency': f"Emergency contraception (P2) can prevent pregnancy if taken within 72 hours of unprotected sex. It's not for regular use.",
            'sterilization_female': f"Tubal ligation is permanent and 99% effective. It's a good choice if you're certain you don't want future children.",
            'sterilization_male': f"Vasectomy is permanent and 99% effective. It's a safe option for men who don't want future children.",
        }
        
        explanation = explanations.get(method_id, f"{method_name} is a good option for you.")
        
        # Add fertility intent context
        if fertility_intent in ['want_soon', 'want_later']:
            explanation += " This method is reversible, preserving your ability to have children in the future."
        elif fertility_intent == 'no_more':
            explanation += " This method is highly effective for permanent pregnancy prevention."
        
        return explanation
    
    def _create_retrieval_query(self, profile: Dict, allowed_methods: List[str]) -> str:
        """Create a query for RAG retrieval"""
        fertility_intent = profile.get('fertility_intent', 'unsure')
        
        intent_text = {
            'want_soon': 'want to have children soon',
            'want_later': 'want to have children in a few years',
            'no_more': 'do not want more children',
            'unsure': 'am unsure about future children'
        }.get(fertility_intent, 'want to prevent pregnancy')
        
        query = f"""
        User is {profile['age']} years old and {intent_text}.
        They need contraceptive recommendations.
        Safe methods include: {', '.join(allowed_methods[:5]) if allowed_methods else 'various methods'}.
        Please provide information about suitable contraceptive methods.
        """
        return query.strip()
    
    def recommend(
        self, 
        user_profile: Dict[str, Any],
        include_educational: bool = True
    ) -> Dict[str, Any]:
        """
        Main entry point - get personalized recommendations
        
        Args:
            user_profile: User health data with fields:
                - age (int)
                - smoking (bool)
                - migraine_type (str)
                - systolic_bp (int)
                - diastolic_bp (int)
                - breastfeeding (bool)
                - postpartum_weeks (int)
                - fertility_intent (str)
            
            include_educational: Whether to include educational content
            
        Returns:
            Dictionary with recommendations, restrictions, and explanations
        """
        print("\n" + "=" * 60)
        print("🎯 Generating Recommendations")
        print("=" * 60)
        
        # Validate required fields
        required = ['age', 'smoking', 'migraine_type', 'systolic_bp', 
                   'diastolic_bp', 'breastfeeding', 'fertility_intent']
        missing = [f for f in required if f not in user_profile]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        # =========================================================
        # STEP 1: Guardrail Safety Check
        # =========================================================
        print("\n🔒 STEP 1: Guardrail Safety Check")
        
        guardrail_result = self.guardrail.evaluate(user_profile)
        
        restricted_methods = guardrail_result['restricted_methods']
        allowed_methods = guardrail_result['allowed_methods']
        requires_provider = guardrail_result['requires_provider']
        
        print(f"   ✅ Allowed methods: {len(allowed_methods)}")
        print(f"   ❌ Restricted methods: {len(restricted_methods)}")
        print(f"   🏥 Provider consultation needed: {requires_provider}")
        
        # If no allowed methods, return early with provider recommendation
        if not allowed_methods:
            return {
                'recommended_methods': [],
                'restricted_methods': self._format_restricted(restricted_methods),
                'requires_provider': True,
                'message': "Based on your health profile, please consult a healthcare provider for personalized contraceptive advice.",
                'timestamp': datetime.now().isoformat()
            }
        
        # =========================================================
        # STEP 2: RAG Knowledge Retrieval (if available)
        # =========================================================
        print("\n📚 STEP 2: Knowledge Retrieval (RAG)")
        
        retrieved_context = None
        if self.rag and include_educational:
            try:
                query = self._create_retrieval_query(user_profile, allowed_methods)
                retrieved_context = self.rag.retrieve_all_relevant(user_profile, allowed_methods)
                print(f"   ✅ Retrieved context with guidelines and myths")
            except Exception as e:
                print(f"   ⚠️ RAG retrieval failed: {e}")
                retrieved_context = None
        else:
            print("   ⚠️ RAG not available - using fallback")
        
        # =========================================================
        # STEP 3: Rank Allowed Methods
        # =========================================================
        print("\n📊 STEP 3: Ranking Methods")
        
        ranked_methods = []
        for method_id in allowed_methods:
            # Get method info
            method_name = self._get_method_name(method_id)
            
            print(f"\n   📌 Evaluating: {method_name}")
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(
                method_id, user_profile, retrieved_context
            )
            
            # Generate explanation
            explanation = self._generate_explanation(
                method_id, method_name, user_profile, confidence, retrieved_context
            )
            
            # Get effectiveness
            effectiveness = self.guardrail.methods.get(method_id, {}).get('effectiveness', 90)
            
            ranked_methods.append({
                'method_id': method_id,
                'method_name': method_name,
                'confidence_score': round(confidence, 1),
                'effectiveness': effectiveness,
                'explanation': explanation,
                'type': self.guardrail.methods.get(method_id, {}).get('type', 'unknown')
            })
        
        # Sort by confidence score (highest first)
        ranked_methods.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        # Get top 5 recommendations
        top_recommendations = ranked_methods[:5]
        
        print(f"\n   ✅ Ranked {len(ranked_methods)} methods")
        if top_recommendations:
            print(f"   🏆 Top recommendation: {top_recommendations[0]['method_name']} ({top_recommendations[0]['confidence_score']:.0f}%)")
        
        # =========================================================
        # STEP 4: Prepare Response
        # =========================================================
        print("\n📤 STEP 4: Preparing Response")
        
        response = {
            'recommended_methods': top_recommendations,
            'restricted_methods': self._format_restricted(restricted_methods),
            'requires_provider': requires_provider,
            'allowed_count': len(allowed_methods),
            'restricted_count': len(restricted_methods),
            'timestamp': datetime.now().isoformat(),
            'disclaimer': "This is not medical advice. Always consult a healthcare provider before starting any contraceptive method."
        }
        
        # Generate summary if RAG available
        if self.rag and retrieved_context and top_recommendations:
            try:
                method_scores = [(m['method_id'], m['confidence_score']) for m in top_recommendations[:3]]
                summary = self.rag.generate_recommendation_context(
                    user_profile, allowed_methods, method_scores
                )
                response['summary'] = summary
            except Exception as e:
                response['summary'] = f"Based on your health profile, {top_recommendations[0]['method_name']} appears to be a good fit for you with {top_recommendations[0]['confidence_score']:.0f}% confidence."
        else:
            if top_recommendations:
                response['summary'] = f"Based on your health profile, {top_recommendations[0]['method_name']} appears to be a good fit for you with {top_recommendations[0]['confidence_score']:.0f}% confidence. Please consult a healthcare provider before making a decision."
        
        print("\n" + "=" * 60)
        print("✅ Recommendations Generated Successfully!")
        print("=" * 60)
        
        return response
    
    def _format_restricted(self, restricted_methods: Dict) -> List[Dict]:
        """Format restricted methods for output"""
        formatted = []
        for method_id, restrictions in restricted_methods.items():
            method_name = self._get_method_name(method_id)
            for r in restrictions:
                formatted.append({
                    'method_id': method_id,
                    'method_name': method_name,
                    'category': r.get('category', 4),
                    'explanation': r.get('explanation', 'Not recommended for you.'),
                    'rule_id': r.get('rule_id', 'UNKNOWN')
                })
        return formatted


# =========================================================
# TESTING THE PIPELINE
# =========================================================

def test_pipeline():
    """Test the complete recommendation pipeline"""
    print("\n" + "=" * 70)
    print("🧪 TESTING COMPLETE RECOMMENDATION PIPELINE")
    print("=" * 70)
    
    # Initialize pipeline
    pipeline = RecommendationPipeline()
    
    # Test profiles
    test_profiles = [
        {
            "name": "Healthy Young Woman",
            "profile": {
                "age": 24,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 110,
                "diastolic_bp": 70,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "want_later"
            }
        },
        {
            "name": "Smoker over 35",
            "profile": {
                "age": 36,
                "smoking": True,
                "migraine_type": "none",
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "no_more"
            }
        },
        {
            "name": "Migraine with Aura",
            "profile": {
                "age": 28,
                "smoking": False,
                "migraine_type": "with_aura",
                "systolic_bp": 115,
                "diastolic_bp": 75,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "want_later"
            }
        }
    ]
    
    for test in test_profiles:
        print("\n" + "=" * 70)
        print(f"👤 TESTING: {test['name']}")
        print("=" * 70)
        
        print("\n📋 User Profile:")
        for key, value in test['profile'].items():
            print(f"   {key}: {value}")
        
        try:
            # Get recommendations
            result = pipeline.recommend(test['profile'])
            
            print("\n📊 RESULTS:")
            print(f"   ✅ Recommended Methods (Top 3):")
            for method in result['recommended_methods'][:3]:
                print(f"      • {method['method_name']} - {method['confidence_score']:.0f}% confidence")
                print(f"        {method['explanation'][:120]}...")
            
            print(f"\n   ❌ Restricted Methods: {result['restricted_count']}")
            for method in result['restricted_methods'][:2]:
                print(f"      • {method['method_name']}: {method['explanation'][:80]}...")
            
            print(f"\n   🏥 Provider Consultation Required: {result['requires_provider']}")
            print(f"   📊 Allowed: {result['allowed_count']}, Restricted: {result['restricted_count']}")
            
            if 'summary' in result:
                print(f"\n   📝 Summary: {result['summary']}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_pipeline()