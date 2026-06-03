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

# Example usage
if __name__ == "__main__":
    guardrail = WHOMECGuardrail()
    
    # Test profile
    test_profile = {
        'age': 36,
        'smoking': True,
        'migraine_type': 'none',
        'systolic_bp': 120,
        'diastolic_bp': 80,
        'breastfeeding': False,
        'postpartum_weeks': 100
    }
    
    result = guardrail.evaluate(test_profile)
    print(json.dumps(result, indent=2))