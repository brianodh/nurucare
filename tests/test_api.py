from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_healthz_returns_ok():
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_intake_endpoint_accepts_profile():
    response = client.post(
        '/api/intake',
        json={
            'age': 25,
            'systolic_bp': 110,
            'diastolic_bp': 70,
            'smoking': False,
            'migraine_type': 'none',
            'breastfeeding': False,
            'postpartum_weeks': 10,
            'duration_pref': 'short_term',
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert 'recommended_methods' in data
    assert 'restricted_methods' in data
    assert 'confidence_score' in data
