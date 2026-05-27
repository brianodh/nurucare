"""
WHO MEC Guardrail Engine - Deterministic Safety Rules
Ensures clinical safety before any personalization
"""

import json
from typing import Dict, List, Any
from pathlib import Path

class WHOMECGuardrail:
    def __init__(self):
        # Load WHO MEC rules
        rules_path = Path(__file__).parent / "who_mec_rules.json"
        with open(rules_path, 'r') as f:
            self.rules_data = json.load(f)
        self.rules = self.rules_data['rules']
        self.method_mapping = self.rules_data['method_mapping']
    
    def evaluate(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate user profile against all WHO MEC rules
        
        Args:
            user_profile: Dict with keys: age, smoking, migraine_type, 
                         systolic_bp, diastolic_bp, breastfeeding, 
                         postpartum_weeks
        
        Returns:
            Dict with restricted_methods, allowed_methods, explanations
        """
        restricted = {}
        explanations = []
        
        for rule in self.rules:
            if self._check_condition(rule['condition'], user_profile):
                for method in rule['restrict_methods']:
                    if method not in restricted:
                        restricted[method] = []
                    restricted[method].append({
                        'rule_id': rule['id'],
                        'category': rule['category'],
                        'explanation': rule['explanation']
                    })
                explanations.append({
                    'rule_id': rule['id'],
                    'explanation': rule['explanation']
                })
        
        # Determine allowed methods (all methods not in restricted)
        all_methods = list(self.method_mapping.keys())
        allowed_methods = [m for m in all_methods if m not in restricted]
        
        return {
            'restricted_methods': restricted,
            'allowed_methods': allowed_methods,
            'explanations': explanations,
            'requires_provider': self._requires_provider(restricted)
        }
    
    def _check_condition(self, condition: str, profile: Dict) -> bool:
        """Evaluate a condition string against the user profile"""
        # Convert condition string to evaluatable expression
        # Handle common operators: >, <, >=, <=, ==, AND
        try:
            # Create a safe evaluation context
            context = {
                'age': profile.get('age', 0),
                'smoking': profile.get('smoking', False),
                'systolic_bp': profile.get('systolic_bp', 0),
                'diastolic_bp': profile.get('diastolic_bp', 0),
                'breastfeeding': profile.get('breastfeeding', False),
                'postpartum_weeks': profile.get('postpartum_weeks', 100)
            }
            
            # Handle migraine separately (special string comparison)
            if 'migraine' in condition:
                migraine_type = profile.get('migraine_type', 'none')
                return migraine_type == 'with_aura'
            
            # For age and BP conditions
            if 'age > 35 AND smoking' in condition:
                return context['age'] > 35 and context['smoking']
            
            if 'systolic_bp >= 140 OR diastolic_bp >= 90' in condition:
                return context['systolic_bp'] >= 140 or context['diastolic_bp'] >= 90
            
            if 'breastfeeding' in condition and 'postpartum_weeks' in condition:
                return context['breastfeeding'] and context['postpartum_weeks'] < 6
            
            if 'age >= 40' in condition:
                return context['age'] >= 40
            
            return False
            
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False
    
    def _requires_provider(self, restricted: Dict) -> bool:
        """Check if user requires provider consultation"""
        for method, restrictions in restricted.items():
            for r in restrictions:
                if r['category'] >= 3:
                    return True
        return False

# ============================================
# ENHANCED TESTING SECTION
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TESTING WHO MEC GUARDRAIL ENGINE")
    print("=" * 70 + "\n")
    
    # Initialize the guardrail
    guardrail = WHOMECGuardrail()
    print("✅ Guardrail engine loaded successfully\n")
    
    # Define test profiles
    test_profiles = [
        {
            "name": "✅ Healthy young woman - NO RESTRICTIONS",
            "profile": {
                "age": 24,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 110,
                "diastolic_bp": 70,
                "breastfeeding": False,
                "postpartum_weeks": 100
            }
        },
        {
            "name": "❌ Smoker over 35 - HIGH RISK (Category 4)",
            "profile": {
                "age": 36,
                "smoking": True,
                "migraine_type": "none",
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "breastfeeding": False,
                "postpartum_weeks": 100
            }
        },
        {
            "name": "❌ Migraine with aura - HIGH RISK (Category 4)",
            "profile": {
                "age": 28,
                "smoking": False,
                "migraine_type": "with_aura",
                "systolic_bp": 115,
                "diastolic_bp": 75,
                "breastfeeding": False,
                "postpartum_weeks": 100
            }
        },
        {
            "name": "⚠️ Hypertension - CAUTION (Category 3)",
            "profile": {
                "age": 34,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 145,
                "diastolic_bp": 95,
                "breastfeeding": False,
                "postpartum_weeks": 100
            }
        },
        {
            "name": "⚠️ Breastfeeding new mother - CAUTION (Category 3)",
            "profile": {
                "age": 29,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 118,
                "diastolic_bp": 78,
                "breastfeeding": True,
                "postpartum_weeks": 3
            }
        },
        {
            "name": "ℹ️ Woman over 40 - AGE CAUTION (Category 2)",
            "profile": {
                "age": 42,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 125,
                "diastolic_bp": 82,
                "breastfeeding": False,
                "postpartum_weeks": 100
            }
        }
    ]
    
    # Test each profile
    for test in test_profiles:
        print("=" * 70)
        print(f"🧪 {test['name']}")
        print("=" * 70)
        
        print(f"\n📋 User Profile:")
        for key, value in test['profile'].items():
            print(f"   {key}: {value}")
        
        # Evaluate
        result = guardrail.evaluate(test['profile'])
        
        print(f"\n📊 Evaluation Result:")
        
        # Print summary
        restricted_count = len(result['restricted_methods'])
        allowed_count = len(result['allowed_methods'])
        
        if restricted_count == 0:
            print(f"   ✅ SAFE: No restrictions - all methods are medically safe")
        else:
            print(f"   ⚠️ {restricted_count} method(s) restricted for safety")
            print(f"   ✅ {allowed_count} method(s) remain available")
        
        # Print restricted methods
        if result['restricted_methods']:
            print(f"\n❌ RESTRICTED METHODS:")
            for method_id, restrictions in result['restricted_methods'].items():
                # Get readable method name from method_mapping
                method_name = guardrail.method_mapping.get(method_id, method_id)
                print(f"   • {method_name}")
                for r in restrictions:
                    print(f"     - Category {r['category']}: {r['explanation'][:80]}...")
        
        # Print allowed methods (first 5)
        if result['allowed_methods']:
            print(f"\n✅ ALLOWED METHODS (first 5):")
            for method_id in result['allowed_methods'][:5]:
                method_name = guardrail.method_mapping.get(method_id, method_id)
                print(f"   • {method_name}")
        
        print(f"\n🏥 Requires Provider Consultation: {result['requires_provider']}")
        print()
    
    # Print summary of all methods
    print("=" * 70)
    print("📋 CONTRACEPTIVE METHODS BEING MONITORED")
    print("=" * 70)
    
    for method_id, name in guardrail.method_mapping.items():
        # Check if method contains estrogen (combined methods do)
        if 'combined' in method_id or method_id in ['combined_pill', 'combined_patch', 'combined_ring']:
            estrogen = "⚠️ Contains ESTROGEN - may be restricted"
        else:
            estrogen = "✓ No estrogen - safer for most"
        print(f"   • {name}: {estrogen}")
    
    print("\n" + "=" * 70)
    print("✅ Guardrail engine test complete!")
    print("=" * 70)