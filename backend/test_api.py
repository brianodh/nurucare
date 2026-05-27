"""
NuruCare - API Tests
Run these to verify all endpoints work
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(response.json())
    print("-" * 50)

def test_intake():
    """Test intake endpoint"""
    data = {
        "age": 28,
        "gender": "female",
        "smoking": False,
        "migraine_type": "none",
        "fertility_intention": "long_term",
        "parity": 1
    }
    response = requests.post(f"{BASE_URL}/api/v1/intake", json=data)
    print(f"Intake Endpoint: {response.status_code}")
    print(response.json())
    print("-" * 50)

def test_recommend():
    """Test recommendation endpoint"""
    data = {
        "age": 28,
        "gender": "female",
        "smoking": False,
        "migraine_type": "none",
        "fertility_intention": "long_term",
        "parity": 1,
        "breastfeeding": False
    }
    response = requests.post(f"{BASE_URL}/api/v1/recommend", json=data)
    print(f"Recommendation Endpoint: {response.status_code}")
    result = response.json()
    print(f"Recommended methods: {len(result.get('recommended_methods', []))}")
    print(f"Restricted methods: {len(result.get('restricted_methods', []))}")
    print(f"Requires consultation: {result.get('requires_provider_consultation')}")
    print("-" * 50)

def test_session_key():
    """Test session key generation"""
    response = requests.post(f"{BASE_URL}/api/v1/session-key")
    print(f"Session Key Endpoint: {response.status_code}")
    print(response.json())
    print("-" * 50)

def test_sync_token():
    """Test sync token generation"""
    response = requests.post(f"{BASE_URL}/api/v1/sync/token")
    print(f"Sync Token Endpoint: {response.status_code}")
    print(response.json())
    print("-" * 50)

def test_edge_cases():
    """Test edge cases for WHO MEC rules"""
    print("Testing Edge Cases:")
    
    # Case 1: Smoker over 35
    data = {
        "age": 36,
        "gender": "female",
        "smoking": True,
        "migraine_type": "none",
        "fertility_intention": "no_more",
        "parity": 2
    }
    response = requests.post(f"{BASE_URL}/api/v1/recommend", json=data)
    print(f"Smoker >35: {response.json().get('restricted_methods', [])}")
    
    # Case 2: Migraine with aura
    data = {
        "age": 25,
        "gender": "female",
        "smoking": False,
        "migraine_type": "with_aura",
        "fertility_intention": "long_term",
        "parity": 0
    }
    response = requests.post(f"{BASE_URL}/api/v1/recommend", json=data)
    print(f"Migraine with aura: {response.json().get('restricted_methods', [])}")
    
    # Case 3: Breastfeeding
    data = {
        "age": 30,
        "gender": "female",
        "smoking": False,
        "migraine_type": "none",
        "fertility_intention": "short_term",
        "parity": 1,
        "breastfeeding": True
    }
    response = requests.post(f"{BASE_URL}/api/v1/recommend", json=data)
    print(f"Breastfeeding: {[m.get('name') for m in response.json().get('recommended_methods', [])]}")
    print("-" * 50)

if __name__ == "__main__":
    print("=" * 50)
    print("Running NuruCare API Tests")
    print("=" * 50 + "\n")
    
    test_health()
    test_intake()
    test_recommend()
    test_session_key()
    test_sync_token()
    test_edge_cases()
    
    print("All tests completed!")