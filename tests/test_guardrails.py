import pytest

from backend.engine.guardrail import WHOMECGuardrail


def test_guardrail_restricts_smoking_over_35():
    guard = WHOMECGuardrail()
    result = guard.evaluate({
        'age': 38,
        'smoking': True,
        'migraine_type': 'none',
        'systolic_bp': 120,
        'diastolic_bp': 80,
        'breastfeeding': False,
        'postpartum_weeks': 100,
    })

    assert 'combined_oral_contraceptives' in result['restricted_methods']
    assert result['requires_provider'] is True


def test_guardrail_allows_non_contraindicated_profile():
    guard = WHOMECGuardrail()
    result = guard.evaluate({
        'age': 28,
        'smoking': False,
        'migraine_type': 'none',
        'systolic_bp': 110,
        'diastolic_bp': 70,
        'breastfeeding': False,
        'postpartum_weeks': 100,
    })

    assert result['requires_provider'] is False
    assert isinstance(result['allowed_methods'], list)
