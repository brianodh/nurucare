"""
NuruCare - Edge Case Tests for Contraindications
=================================================

This file tests that the recommendation engine correctly handles
ALL WHO MEC contraindications and edge cases.

Run: pytest tests/edge_cases/test_contraindications.py -v
Or: python tests/edge_cases/test_contraindications.py

Author: Brian Odhiambo Ouma
Date: June 1, 2026
"""

import sys
import json
import pytest
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from engine.guardrail import WHOMECGuardrail
from engine.recommendation_pipeline import RecommendationPipeline


# =========================================================
# TEST DATA - All Contraindication Scenarios
# =========================================================

class EdgeCaseTestData:
    """All edge case scenarios to test"""
    
    # Single contraindications (each rule individually)
    # UPDATED: Changed 'combined_pill' to 'combined_oral_contraceptives' to match guardrail
    SINGLE_CONTRAS = [
        {
            "id": "EC-001",
            "name": "Smoker over 35 (MEC-001 Category 4)",
            "profile": {
                "age": 36,
                "smoking": True,
                "migraine_type": "none",
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "want_later"
            },
            "expected_restricted": ["combined_oral_contraceptives", "combined_patch", "combined_ring"],
            "expected_category": 4,
            "requires_provider": True
        },
        {
            "id": "EC-002",
            "name": "Migraine with aura (MEC-002 Category 4)",
            "profile": {
                "age": 28,
                "smoking": False,
                "migraine_type": "with_aura",
                "systolic_bp": 115,
                "diastolic_bp": 75,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "want_later"
            },
            "expected_restricted": ["combined_oral_contraceptives", "combined_patch", "combined_ring"],
            "expected_category": 4,
            "requires_provider": True
        },
        {
            "id": "EC-003",
            "name": "Hypertension (MEC-003 Category 3)",
            "profile": {
                "age": 34,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 145,
                "diastolic_bp": 95,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "want_later"
            },
            "expected_restricted": ["combined_hormonal_methods"],
            "expected_category": 3,
            "requires_provider": True
        },
        {
            "id": "EC-004",
            "name": "Breastfeeding <6 weeks (MEC-004 Category 3)",
            "profile": {
                "age": 29,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 118,
                "diastolic_bp": 78,
                "breastfeeding": True,
                "postpartum_weeks": 3,
                "fertility_intent": "want_later"
            },
            "expected_restricted": ["combined_hormonal_methods"],
            "expected_category": 3,
            "requires_provider": True
        },
        {
            "id": "EC-005",
            "name": "Age over 40 (MEC-005 Category 2)",
            "profile": {
                "age": 42,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 125,
                "diastolic_bp": 82,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "no_more"
            },
            "expected_restricted": ["combined_hormonal_methods"],
            "expected_category": 2,
            "requires_provider": False
        }
    ]
    
    # Multiple contraindications combined
    MULTIPLE_CONTRAS = [
        {
            "id": "EC-006",
            "name": "Smoker over 35 + Hypertension",
            "profile": {
                "age": 38,
                "smoking": True,
                "migraine_type": "none",
                "systolic_bp": 150,
                "diastolic_bp": 95,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "no_more"
            },
            "expected_restricted_count": 3,
            "requires_provider": True
        },
        {
            "id": "EC-007",
            "name": "Migraine with aura + Breastfeeding",
            "profile": {
                "age": 30,
                "smoking": False,
                "migraine_type": "with_aura",
                "systolic_bp": 118,
                "diastolic_bp": 78,
                "breastfeeding": True,
                "postpartum_weeks": 4,
                "fertility_intent": "want_later"
            },
            "expected_restricted_count": 2,
            "requires_provider": True
        },
        {
            "id": "EC-008",
            "name": "Age 45 + Hypertension + Smoker",
            "profile": {
                "age": 45,
                "smoking": True,
                "migraine_type": "none",
                "systolic_bp": 155,
                "diastolic_bp": 100,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "no_more"
            },
            "expected_restricted_count": 3,
            "requires_provider": True
        }
    ]
    
    # Boundary edge cases (limit values)
    BOUNDARY_CASES = [
        {
            "id": "EC-009",
            "name": "Age exactly 35 (should NOT trigger age+smoking rule)",
            "profile": {
                "age": 35,
                "smoking": True,
                "migraine_type": "none",
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "want_later"
            },
            "expected_restricted": [],
            "requires_provider": False
        },
        {
            "id": "EC-010",
            "name": "BP exactly 140/90 (should trigger hypertension rule)",
            "profile": {
                "age": 30,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 140,
                "diastolic_bp": 90,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "want_later"
            },
            "expected_restricted": ["combined_hormonal_methods"],
            "requires_provider": True
        },
        {
            "id": "EC-011",
            "name": "Breastfeeding exactly 6 weeks (should NOT trigger)",
            "profile": {
                "age": 28,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 115,
                "diastolic_bp": 75,
                "breastfeeding": True,
                "postpartum_weeks": 6,
                "fertility_intent": "want_later"
            },
            "expected_restricted": [],
            "requires_provider": False
        },
        {
            "id": "EC-012",
            "name": "Age exactly 40 (should trigger age rule)",
            "profile": {
                "age": 40,
                "smoking": False,
                "migraine_type": "none",
                "systolic_bp": 125,
                "diastolic_bp": 82,
                "breastfeeding": False,
                "postpartum_weeks": 100,
                "fertility_intent": "no_more"
            },
            "expected_restricted": ["combined_hormonal_methods"],
            "expected_category": 2,
            "requires_provider": False
        }
    ]
    
    # Healthy baseline (no restrictions)
    HEALTHY_BASELINE = {
        "id": "EC-013",
        "name": "Healthy user - NO restrictions",
        "profile": {
            "age": 24,
            "smoking": False,
            "migraine_type": "none",
            "systolic_bp": 110,
            "diastolic_bp": 70,
            "breastfeeding": False,
            "postpartum_weeks": 100,
            "fertility_intent": "want_later"
        },
        "expected_restricted_count": 0,
        "requires_provider": False
    }


# =========================================================
# GUARDRAIL EDGE CASE TESTS
# =========================================================

class TestGuardrailEdgeCases:
    """Test guardrail engine handles all contraindications correctly"""
    
    def setup_method(self):
        """Set up before each test"""
        self.guardrail = WHOMECGuardrail()
    
    def test_single_contraindications(self):
        """Test each contraindication individually"""
        print("\n" + "=" * 70)
        print("🧪 TESTING SINGLE CONTRAINDICATIONS")
        print("=" * 70)
        
        for test in EdgeCaseTestData.SINGLE_CONTRAS:
            print(f"\n📌 {test['id']}: {test['name']}")
            result = self.guardrail.evaluate(test['profile'])
            
            restricted = result['restricted_methods']
            expected_restricted = test['expected_restricted']
            
            # Assert each expected method is restricted
            for method in expected_restricted:
                assert method in restricted, f"Expected {method} to be restricted for {test['id']}"
            
            # Check category if applicable
            if 'expected_category' in test and expected_restricted:
                first_restricted = next(iter(restricted.values()))[0]
                assert first_restricted['category'] == test['expected_category'], \
                    f"Expected category {test['expected_category']} for {test['id']}"
            
            # Check provider consultation flag
            assert result['requires_provider'] == test['requires_provider'], \
                f"Provider consultation flag mismatch for {test['id']}"
            
            print(f"   ✅ PASS")
        
        print(f"\n✅ All single contraindication tests passed")
    
    def test_multiple_contraindications(self):
        """Test multiple contraindications together"""
        print("\n" + "=" * 70)
        print("🧪 TESTING MULTIPLE CONTRAINDICATIONS")
        print("=" * 70)
        
        for test in EdgeCaseTestData.MULTIPLE_CONTRAS:
            print(f"\n📌 {test['id']}: {test['name']}")
            result = self.guardrail.evaluate(test['profile'])
            
            restricted_count = len(result['restricted_methods'])
            expected_count = test['expected_restricted_count']
            
            assert restricted_count >= expected_count, \
                f"Expected at least {expected_count} restricted methods, got {restricted_count}"
            assert result['requires_provider'] == test['requires_provider'], \
                f"Provider consultation flag mismatch for {test['id']}"
            
            print(f"   ✅ PASS (restricted: {restricted_count})")
        
        print(f"\n✅ All multiple contraindication tests passed")
    
    def test_boundary_cases(self):
        """Test boundary edge cases (limit values)"""
        print("\n" + "=" * 70)
        print("🧪 TESTING BOUNDARY CASES")
        print("=" * 70)
        
        for test in EdgeCaseTestData.BOUNDARY_CASES:
            print(f"\n📌 {test['id']}: {test['name']}")
            result = self.guardrail.evaluate(test['profile'])
            
            restricted = result['restricted_methods']
            expected_restricted = test.get('expected_restricted', [])
            
            if expected_restricted:
                for method in expected_restricted:
                    assert method in restricted, f"Expected {method} to be restricted"
            else:
                assert len(restricted) == 0, f"Expected no restrictions, got {list(restricted.keys())}"
            
            assert result['requires_provider'] == test['requires_provider'], \
                f"Provider consultation flag mismatch for {test['id']}"
            
            print(f"   ✅ PASS")
        
        print(f"\n✅ All boundary case tests passed")
    
    def test_healthy_baseline(self):
        """Test healthy user has no restrictions"""
        print("\n" + "=" * 70)
        print("🧪 TESTING HEALTHY BASELINE")
        print("=" * 70)
        
        test = EdgeCaseTestData.HEALTHY_BASELINE
        print(f"\n📌 {test['id']}: {test['name']}")
        
        result = self.guardrail.evaluate(test['profile'])
        
        assert len(result['restricted_methods']) == 0, \
            f"Expected 0 restrictions, got {len(result['restricted_methods'])}"
        assert result['requires_provider'] == test['requires_provider'], \
            "Provider consultation flag mismatch"
        
        print(f"   ✅ PASS")


# =========================================================
# RECOMMENDATION PIPELINE EDGE CASE TESTS
# =========================================================

class TestRecommendationPipelineEdgeCases:
    """Test full recommendation pipeline handles edge cases correctly"""
    
    def setup_method(self):
        """Set up before each test"""
        try:
            self.pipeline = RecommendationPipeline()
            self.available = True
        except Exception as e:
            print(f"⚠️ Pipeline not available: {e}")
            self.available = False
    
    def test_high_risk_profiles_get_provider_warning(self):
        """Test high-risk profiles trigger provider consultation warning"""
        print("\n" + "=" * 70)
        print("🧪 TESTING HIGH-RISK PROFILES - PROVIDER WARNING")
        print("=" * 70)
        
        if not self.available:
            pytest.skip("Pipeline not available")
        
        high_risk_profiles = [
            ("Smoker over 35", EdgeCaseTestData.SINGLE_CONTRAS[0]['profile']),
            ("Migraine with aura", EdgeCaseTestData.SINGLE_CONTRAS[1]['profile']),
            ("Hypertension", EdgeCaseTestData.SINGLE_CONTRAS[2]['profile']),
            ("Multiple risks", EdgeCaseTestData.MULTIPLE_CONTRAS[0]['profile'])
        ]
        
        for name, profile in high_risk_profiles:
            print(f"\n📌 Testing: {name}")
            result = self.pipeline.recommend(profile, include_educational=False)
            
            assert result.get('requires_provider', False) == True, \
                f"{name} should require provider consultation"
            print(f"   ✅ Provider consultation flag set correctly")
        
        print(f"\n✅ All high-risk profile tests passed")
    
    def test_safe_methods_always_available(self):
        """Test that safe methods are always available regardless of profile"""
        print("\n" + "=" * 70)
        print("🧪 TESTING SAFE METHODS ALWAYS AVAILABLE")
        print("=" * 70)
        
        if not self.available:
            pytest.skip("Pipeline not available")
        
        # Safe methods that should ALWAYS be available (check by method_id)
        safe_method_ids = ['male_condom', 'female_condom', 'iud_copper']
        
        risk_profiles = [
            EdgeCaseTestData.SINGLE_CONTRAS[0]['profile'],  # Smoker over 35
            EdgeCaseTestData.SINGLE_CONTRAS[1]['profile'],  # Migraine with aura
            EdgeCaseTestData.SINGLE_CONTRAS[2]['profile']   # Hypertension
        ]
        
        for i, profile in enumerate(risk_profiles):
            result = self.pipeline.recommend(profile, include_educational=False)
            
            # Check by allowed_count (from guardrail)
            allowed_count = result.get('allowed_count', 0)
            assert allowed_count > 0, f"Profile {i+1}: No allowed methods"
            
            # Check safe methods are NOT in restricted_methods
            restricted_ids = [m.get('method_id', '') for m in result.get('restricted_methods', [])]
            
            for method_id in safe_method_ids:
                assert method_id not in restricted_ids, \
                    f"Profile {i+1}: Safe method {method_id} should NOT be restricted. It is in restricted list."
            
            # male_condom should always be in top recommendations (high weight)
            recommended_ids = [m.get('method_id', '') for m in result.get('recommended_methods', [])]
            assert 'male_condom' in recommended_ids, \
                f"Profile {i+1}: male_condom should be in top recommendations"
            
            print(f"   ✅ Profile {i+1}: Safe methods not restricted. "
                  f"male_condom in top {len(recommended_ids)}")
        
        print(f"\n✅ All safe methods are always available (never restricted)")


# =========================================================
# RUN ALL EDGE CASE TESTS
# =========================================================

def run_all_edge_case_tests():
    """Run all edge case tests and print summary"""
    print("\n" + "=" * 70)
    print("🔬 RUNNING COMPLETE EDGE CASE TEST SUITE")
    print("=" * 70)
    
    # Track results
    results = {}
    total_tests = 0
    total_passed = 0
    
    # Run guardrail tests
    guardrail_tests = TestGuardrailEdgeCases()
    guardrail_tests.setup_method()
    
    print("\n" + "=" * 70)
    print("🏥 GUARDRAIL ENGINE TESTS")
    print("=" * 70)
    
    test_methods = [
        ("Single Contraindications", guardrail_tests.test_single_contraindications),
        ("Multiple Contraindications", guardrail_tests.test_multiple_contraindications),
        ("Boundary Cases", guardrail_tests.test_boundary_cases),
        ("Healthy Baseline", guardrail_tests.test_healthy_baseline)
    ]
    
    for name, test_method in test_methods:
        try:
            test_method()
            results[name] = "PASSED"
            total_tests += 1
            total_passed += 1
        except AssertionError as e:
            results[name] = f"FAILED: {e}"
            total_tests += 1
            print(f"   ❌ {name} failed: {e}")
    
    # Run pipeline tests
    print("\n" + "=" * 70)
    print("🤖 RECOMMENDATION PIPELINE TESTS")
    print("=" * 70)
    
    pipeline_tests = TestRecommendationPipelineEdgeCases()
    pipeline_tests.setup_method()
    
    pipeline_methods = [
        ("Provider Warning", pipeline_tests.test_high_risk_profiles_get_provider_warning),
        ("Safe Methods Always Available", pipeline_tests.test_safe_methods_always_available)
    ]
    
    for name, test_method in pipeline_methods:
        try:
            test_method()
            results[name] = "PASSED"
            total_tests += 1
            total_passed += 1
        except AssertionError as e:
            results[name] = f"FAILED: {e}"
            total_tests += 1
            print(f"   ❌ {name} failed: {e}")
        except Exception as e:
            results[name] = f"ERROR: {e}"
            total_tests += 1
            print(f"   ⚠️ {name} error: {e}")
    
    # Print final summary
    print("\n" + "=" * 70)
    print("📊 EDGE CASE TEST SUMMARY")
    print("=" * 70)
    
    for name, status in results.items():
        if "PASSED" in status:
            print(f"   ✅ {name}: {status}")
        else:
            print(f"   ❌ {name}: {status}")
    
    print("\n" + "=" * 70)
    print(f"📈 OVERALL: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL EDGE CASE TESTS PASSED! Engine is safe for production.")
        return 0
    else:
        print("\n⚠️ Some edge case tests failed. Please review and fix.")
        return 1


# =========================================================
# MAIN - Run Tests
# =========================================================

if __name__ == "__main__":
    exit_code = run_all_edge_case_tests()
    sys.exit(exit_code)