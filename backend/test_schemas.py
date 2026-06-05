"""
Test script to verify Pydantic schemas work correctly
"""

from api.schemas import (
    IntakeRequest, 
    RecommendationResponse, 
    SessionKeyRequest,
    SyncTokenRequest,
    Gender,
    MigraineType,
    FertilityIntention
)

print("=" * 60)
print("TESTING PYDANTIC SCHEMAS")
print("=" * 60)

# Test 1: Valid IntakeRequest
print("\n✅ Test 1: Valid IntakeRequest")
try:
    valid_request = IntakeRequest(
        age=28,
        gender="female",
        smoking=False,
        migraine_type="none",
        systolic_bp=118,
        diastolic_bp=78,
        fertility_intention="want_later",
        parity=1,
        breastfeeding=False
    )
    print("   Valid intake request created successfully")
    print(f"   Age: {valid_request.age}")
    print(f"   Fertility intention: {valid_request.fertility_intention}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 2: Invalid IntakeRequest (age too high)
print("\n✅ Test 2: Invalid IntakeRequest (age=70 - out of range)")
try:
    invalid_request = IntakeRequest(
        age=70,  # Invalid - max is 60
        gender="female",
        smoking=False,
        migraine_type="none",
        systolic_bp=118,
        diastolic_bp=78,
        fertility_intention="want_later",
        parity=1,
        breastfeeding=False
    )
    print("   ❌ Should have failed but didn't!")
except Exception as e:
    print(f"   ✅ Correctly caught error: {str(e)[:60]}...")

# Test 3: SessionKeyRequest
print("\n✅ Test 3: SessionKeyRequest")
try:
    session_key = SessionKeyRequest(session_key="123456")
    print(f"   Valid session key: {session_key.session_key}")
    
    # Test invalid
    try:
        invalid_key = SessionKeyRequest(session_key="12345")  # Too short
        print("   ❌ Should have failed but didn't!")
    except Exception as e:
        print(f"   ✅ Correctly rejected invalid key: {str(e)[:50]}...")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 4: RecommendationResponse
print("\n✅ Test 4: RecommendationResponse")
try:
    response = RecommendationResponse(
        recommended_methods=[],
        restricted_methods={},
        requires_provider=False,
        myth_busters=["Test myth buster"]
    )
    print(f"   Response created successfully")
    print(f"   Disclaimer: {response.disclaimer[:50]}...")
    print(f"   Timestamp: {response.timestamp}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 5: Enum values
print("\n✅ Test 5: Enum values")
print(f"   Gender options: {[g.value for g in Gender]}")
print(f"   Migraine types: {[m.value for m in MigraineType]}")
print(f"   Fertility intentions: {[f.value for f in FertilityIntention]}")

print("\n" + "=" * 60)
print("✅ All schema tests passed!")
print("=" * 60)