"""
NuruCare - Complete Recommendation Pipeline
===========================================

This module combines the WHO MEC Guardrail Engine with the RAG Pipeline
to produce safe, personalized contraceptive recommendations.

Pipeline Flow:
1. Guardrail evaluates safety -> restricts unsafe methods
2. RAG retrieves knowledge and ranks allowed methods
3. Pipeline combines results into final response
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import guardrail engine
from backend.engine.guardrail import WHOMECGuardrail


class RecommendationPipeline:
    """
    Complete recommendation pipeline combining Guardrail + RAG
    """
    
    def __init__(self):
        """Initialize the pipeline with all components"""
        print("=" * 60)
        print("🚀 Initializing NuruCare Recommendation Pipeline")
        print("=" * 60)
        
        # Initialize guardrail engine
        self.guardrail = WHOMECGuardrail()
        print("✅ Guardrail engine loaded")
        
        # Build methods dictionary from guardrail's method_mapping
        self.method_mapping = self.guardrail.method_mapping
        print(f"✅ Loaded method mapping with {len(self.method_mapping)} methods")
        
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
            'combined_oral_contraceptives': 0.222,
            'implants': 0.157,
            'injectables': 0.152,
            'iud_copper': 0.021,
            'iud_hormonal': 0.018,
            'progestin_only_pill': 0.012,
            'female_condom': 0.008,
            'emergency_contraception': 0.005,
            'withdrawal': 0.002,
            'rhythm': 0.001,
            'lam': 0.001,
            'female_sterilization': 0.001,
            'male_sterilization': 0.0005,
            'combined_patch': 0.0005,
            'combined_ring': 0.0005,
        }
    
    def _get_method_name(self, method_id: str) -> str:
        """Get readable method name from method_mapping"""
        return self.method_mapping.get(method_id, method_id.replace('_', ' ').title())
    
    def _calculate_confidence_score(
        self, 
        method_id: str, 
        user_profile: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score (0-100) for a method
        
        Factors:
        - Medical fit (method is allowed = 40 points)
        - Popularity weight (from real adoption data = 30 points)
        - User preference match (fertility intent = 30 points)
        """
        score = 40.0  # Base medical fit
        
        # Factor 2: Popularity weight (30 points)
        popularity = self.method_weights.get(method_id, 0.01)
        score += popularity * 30
        
        # Factor 3: User preference match (30 points)
        fertility_intent = user_profile.get('fertility_intent', 'unsure')
        score += self._match_fertility_intent(method_id, fertility_intent) * 30
        
        return min(100, max(0, score))
    
    def _match_fertility_intent(self, method_id: str, intent: str) -> float:
        """
        Match method to fertility intent
        1.0 = perfect match, 0.5 = acceptable, 0.0 = poor match
        """
        # Methods that preserve fertility (reversible)
        reversible_methods = [
            'male_condom', 'female_condom', 'combined_oral_contraceptives', 'progestin_only_pill',
            'injectables', 'implants', 'iud_copper', 'iud_hormonal',
            'withdrawal', 'rhythm', 'lam', 'emergency_contraception'
        ]
        
        # Permanent methods (sterilization)
        permanent_methods = ['female_sterilization', 'male_sterilization']
        
        if intent in ['want_soon', 'want_later']:
            if method_id in reversible_methods:
                return 1.0
            elif method_id in permanent_methods:
                return 0.0
            else:
                return 0.5
                
        elif intent == 'no_more':
            if method_id in permanent_methods:
                return 1.0
            elif method_id in reversible_methods:
                return 0.7
            else:
                return 0.5
                
        else:
            return 0.5
    
    def _generate_explanation(
        self, 
        method_id: str, 
        method_name: str,
        user_profile: Dict[str, Any],
        confidence_score: float
    ) -> str:
        """Generate user-friendly explanation for recommendation"""
        fertility_intent = user_profile.get('fertility_intent', 'unsure')
        
        explanations = {
            'implants': f"The implant is 99% effective and lasts 3-5 years. It's reversible and requires no daily action.",
            'iud_copper': f"The copper IUD is 99% effective and lasts up to 10 years. It contains no hormones.",
            'iud_hormonal': f"The hormonal IUD is 99% effective and lasts 3-7 years. It often makes periods lighter.",
            'injectables': f"The injection is 94% effective and requires a shot every 3 months.",
            'combined_oral_contraceptives': f"The combined pill is 93% effective when taken daily. It can make periods lighter.",
            'progestin_only_pill': f"The mini-pill is 93% effective and safe if you can't take estrogen.",
            'male_condom': f"Condoms are 85% effective and also protect against STIs including HIV.",
            'female_condom': f"Female condoms are 79% effective and also protect against STIs.",
            'withdrawal': f"Withdrawal is 78% effective when done correctly every time.",
            'rhythm': f"The rhythm method is 76% effective when you track your cycle accurately.",
            'lam': f"LAM is 98% effective for exclusively breastfeeding mothers.",
            'emergency_contraception': f"Emergency contraception can prevent pregnancy if taken within 72 hours.",
            'female_sterilization': f"Tubal ligation is permanent and 99% effective.",
            'male_sterilization': f"Vasectomy is permanent and 99% effective.",
        }
        
        explanation = explanations.get(method_id, f"{method_name} is a good option for you.")
        
        if fertility_intent in ['want_soon', 'want_later']:
            explanation += " This method is reversible, preserving your ability to have children."
        elif fertility_intent == 'no_more':
            explanation += " This method is highly effective for permanent prevention."
        
        explanation += f" (Confidence: {confidence_score:.0f}%)"
        
        return explanation
    
    def recommend(
        self, 
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point - get personalized recommendations
        """
        print("\n" + "=" * 60)
        print("🎯 Generating Recommendations")
        print("=" * 60)
        
        # STEP 1: Guardrail Safety Check
        print("\n🔒 STEP 1: Guardrail Safety Check")
        
        guardrail_result = self.guardrail.evaluate(user_profile)
        
        restricted_methods = guardrail_result['restricted_methods']
        allowed_methods = guardrail_result['allowed_methods']
        requires_provider = guardrail_result['requires_provider']
        
        print(f"   ✅ Allowed methods: {len(allowed_methods)}")
        print(f"   ❌ Restricted methods: {len(restricted_methods)}")
        print(f"   🏥 Provider consultation needed: {requires_provider}")
        
        if not allowed_methods:
            return {
                'recommended_methods': [],
                'restricted_methods': restricted_methods,
                'requires_provider': True,
                'message': "Please consult a healthcare provider.",
                'timestamp': datetime.now().isoformat()
            }
        
        # STEP 2: Rank Allowed Methods
        print("\n📊 STEP 2: Ranking Methods")
        
        ranked_methods = []
        for method_id in allowed_methods:
            method_name = self._get_method_name(method_id)
            confidence = self._calculate_confidence_score(method_id, user_profile)
            explanation = self._generate_explanation(method_id, method_name, user_profile, confidence)
            
            ranked_methods.append({
                'method_id': method_id,
                'method_name': method_name,
                'confidence_score': confidence,
                'explanation': explanation
            })
        
        ranked_methods.sort(key=lambda x: x['confidence_score'], reverse=True)
        top_recommendations = ranked_methods[:5]
        
        print(f"   ✅ Ranked {len(ranked_methods)} methods")
        if top_recommendations:
            print(f"   🏆 Top: {top_recommendations[0]['method_name']} ({top_recommendations[0]['confidence_score']:.0f}%)")
        
        # STEP 3: Format Response
        print("\n📤 STEP 3: Preparing Response")
        
        formatted_restricted = []
        for method_id, restrictions in restricted_methods.items():
            method_name = self._get_method_name(method_id)
            for r in restrictions:
                formatted_restricted.append({
                    'method_id': method_id,
                    'method_name': method_name,
                    'category': r['category'],
                    'explanation': r['explanation'],
                    'rule_id': r['rule_id']
                })
        
        response = {
            'recommended_methods': top_recommendations,
            'restricted_methods': formatted_restricted,
            'requires_provider': requires_provider,
            'allowed_count': len(allowed_methods),
            'restricted_count': len(restricted_methods),
            'timestamp': datetime.now().isoformat(),
            'disclaimer': "Not medical advice. Consult a healthcare provider."
        }
        
        print("\n" + "=" * 60)
        print("✅ Recommendations Generated!")
        print("=" * 60)
        
        return response


def test_pipeline():
    """Test the complete recommendation pipeline"""
    print("\n" + "=" * 70)
    print("🧪 TESTING COMPLETE RECOMMENDATION PIPELINE")
    print("=" * 70)
    
    pipeline = RecommendationPipeline()
    
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
        }
    ]
    
    for test in test_profiles:
        print("\n" + "=" * 70)
        print(f"👤 TESTING: {test['name']}")
        print("=" * 70)
        
        print("\n📋 User Profile:")
        for key, value in test['profile'].items():
            print(f"   {key}: {value}")
        
        result = pipeline.recommend(test['profile'])
        
        print("\n📊 RESULTS:")
        print(f"   ✅ Top 3 Recommendations:")
        for method in result['recommended_methods'][:3]:
            print(f"      • {method['method_name']} - {method['confidence_score']:.0f}%")
        
        print(f"\n   ❌ Restricted: {len(result['restricted_methods'])} methods")
        print(f"   🏥 Provider: {result['requires_provider']}")


if __name__ == "__main__":
    test_pipeline()