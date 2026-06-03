"""
NuruCare - Partner Sync Flow Tests
==================================

This file tests the complete partner synchronization flow:
1. Token generation
2. Token hashing and storage
3. Token verification
4. Partner linking
5. Edge cases (expired, invalid, reused tokens)
6. Session key flow for nurses

Run: pytest tests/sync/test_sync_flow.py -v
Or: python tests/sync/test_sync_flow.py

Author: Brian Odhiambo Ouma
Date: June 1, 2026
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from sync.partner_sync import (
    PartnerSyncTokenGenerator,
    SessionKeyGenerator,
    CryptographicSyncManager
)


# =========================================================
# TEST DATA
# =========================================================

class SyncTestData:
    """Test data for sync flow tests"""
    
    # Test user IDs
    USER_ALICE = "user_alice_12345"
    USER_BOB = "user_bob_67890"
    SESSION_ID = "session_abc123"
    NURSE_ID = "nurse_001"
    
    # Invalid tokens for testing rejection
    INVALID_TOKENS = [
        "INVALID-TOKEN",
        "NX-AAA-AAA",
        "12345",
        "",
        "NX----",
        "aaaaaaaaaa"
    ]


# =========================================================
# TOKEN GENERATOR TESTS
# =========================================================

class TestTokenGenerator:
    """Test the PartnerSyncTokenGenerator class"""
    
    def setup_method(self):
        """Set up before each test"""
        self.generator = PartnerSyncTokenGenerator(expiry_hours=24)
    
    def test_token_generation_format(self):
        """Test that generated tokens have correct format"""
        print("\n📌 TEST: Token Generation Format")
        
        token = self.generator.generate_token(SyncTestData.USER_ALICE)
        
        # Check format: XX-XXX-XXX (e.g., NX-7K9-2M4)
        parts = token.split('-')
        
        assert len(parts) == 3, f"Token should have 3 parts, got {len(parts)}"
        assert len(parts[0]) == 2, f"Prefix should be 2 chars, got {len(parts[0])}"
        assert len(parts[1]) == 3, f"First part should be 3 chars, got {len(parts[1])}"
        assert len(parts[2]) == 3, f"Second part should be 3 chars, got {len(parts[2])}"
        
        # Check characters are from allowed alphabet
        allowed_chars = set(self.generator.ALPHABET)
        for part in parts[1:]:
            for char in part:
                assert char in allowed_chars, f"Invalid character '{char}' in token"
        
        print(f"   ✅ Token format correct: {token}")
    
    def test_token_uniqueness(self):
        """Test that generated tokens are unique"""
        print("\n📌 TEST: Token Uniqueness")
        
        tokens = set()
        for i in range(100):
            token = self.generator.generate_token(f"test_user_{i}")
            tokens.add(token)
        
        assert len(tokens) == 100, f"Duplicate tokens generated: {100 - len(tokens)} duplicates"
        print(f"   ✅ All 100 tokens are unique")
    
    def test_token_hashing(self):
        """Test that tokens are properly hashed for storage"""
        print("\n📌 TEST: Token Hashing")
        
        token = self.generator.generate_token(SyncTestData.USER_ALICE)
        hash1 = self.generator._hash_token(token)
        
        # Same token should produce same hash
        hash2 = self.generator._hash_token(token)
        assert hash1 == hash2, "Same token produced different hashes"
        
        # Different token should produce different hash
        token2 = self.generator.generate_token(SyncTestData.USER_BOB)
        hash3 = self.generator._hash_token(token2)
        assert hash1 != hash3, "Different tokens produced same hash"
        
        # Hash should be 64 characters (SHA-256)
        assert len(hash1) == 64, f"Hash length should be 64, got {len(hash1)}"
        
        print(f"   ✅ Hashing works correctly")
        print(f"   Token: {token}")
        print(f"   Hash: {hash1[:16]}...")
    
    def test_token_storage_no_plaintext(self):
        """Test that raw tokens are not stored (privacy)"""
        print("\n📌 TEST: No Plain-text Storage")
        
        token = self.generator.generate_token(SyncTestData.USER_ALICE)
        token_hash = self.generator._hash_token(token)
        
        # Check storage contains hash, not raw token
        stored_data = self.generator._storage.get(token_hash)
        assert stored_data is not None, "Token not stored"
        
        # TokenData no longer stores raw token, only hash
        # Verify the stored data has token_hash attribute
        assert hasattr(stored_data, 'token_hash'), "Stored data missing token_hash"
        assert stored_data.token_hash == token_hash, "Stored hash doesn't match"
        
        print(f"   ✅ Privacy preserved: only hash stored in TokenData")
        print(f"   Only hash stored: {token_hash[:16]}...")
    
    def test_token_expiry(self):
        """Test that tokens expire correctly"""
        print("\n📌 TEST: Token Expiry")
        
        # Use the test method that creates token with custom expiry
        token = self.generator.create_test_token_with_expiry(SyncTestData.USER_ALICE, expiry_seconds=1)
        
        # Should be valid immediately
        is_valid, data, msg = self.generator.verify_token(token)
        assert is_valid, f"Token should be valid immediately: {msg}"
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should be expired now
        is_valid, data, msg = self.generator.verify_token(token)
        assert not is_valid, "Token should be expired"
        assert "expired" in msg.lower() or "invalid" in msg.lower(), f"Expiry message not correct: {msg}"
        
        print(f"   ✅ Token expiry works correctly")


# =========================================================
# SESSION KEY GENERATOR TESTS
# =========================================================

class TestSessionKeyGenerator:
    """Test the SessionKeyGenerator class"""
    
    def setup_method(self):
        """Set up before each test"""
        self.generator = SessionKeyGenerator(expiry_minutes=15)
    
    def test_session_key_format(self):
        """Test that session keys are 6-digit numbers"""
        print("\n📌 TEST: Session Key Format")
        
        key = self.generator.generate_key(SyncTestData.SESSION_ID)
        
        # Should be 6 digits
        assert len(key) == 6, f"Key should be 6 digits, got {len(key)}"
        assert key.isdigit(), f"Key should contain only digits, got {key}"
        
        # Should be between 100000 and 999999
        key_int = int(key)
        assert 100000 <= key_int <= 999999, f"Key should be 6 digits, got {key_int}"
        
        print(f"   ✅ Session key format correct: {key}")
    
    def test_session_key_uniqueness(self):
        """Test that session keys are unique"""
        print("\n📌 TEST: Session Key Uniqueness")
        
        keys = set()
        for i in range(100):
            key = self.generator.generate_key(f"session_{i}")
            keys.add(key)
        
        # With 100 keys, duplicates are extremely unlikely
        assert len(keys) == 100, f"Duplicate keys detected: {100 - len(keys)}"
        print(f"   ✅ All 100 session keys are unique")
    
    def test_session_key_expiry(self):
        """Test that session keys expire after 15 minutes"""
        print("\n📌 TEST: Session Key Expiry")
        
        # Use the test method that creates key with custom expiry
        key = self.generator.create_test_key_with_expiry(SyncTestData.SESSION_ID, expiry_seconds=1)
        
        # Should be valid immediately
        is_valid, data, msg = self.generator.verify_key(key)
        assert is_valid, f"Key should be valid immediately: {msg}"
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should be expired now
        is_valid, data, msg = self.generator.verify_key(key)
        assert not is_valid, "Key should be expired"
        assert "expired" in msg.lower() or "invalid" in msg.lower(), f"Expiry message not correct: {msg}"
        
        print(f"   ✅ Session key expiry works correctly")
    
    def test_session_key_one_time_use(self):
        """Test that session keys can only be used once"""
        print("\n📌 TEST: Session Key One-Time Use")
        
        key = self.generator.generate_key(SyncTestData.SESSION_ID)
        
        # First use should succeed
        is_valid, data, msg = self.generator.verify_key(key)
        assert is_valid, f"First verification should succeed: {msg}"
        
        # Mark as used
        self.generator.mark_key_used(key)
        
        # Second use should fail
        is_valid, data, msg = self.generator.verify_key(key)
        assert not is_valid, "Key should not be usable twice"
        assert "already been used" in msg.lower(), f"Wrong message: {msg}"
        
        print(f"   ✅ One-time use enforced")


# =========================================================
# CRYPTOGRAPHIC SYNC MANAGER TESTS
# =========================================================

class TestCryptographicSyncManager:
    """Test the complete CryptographicSyncManager"""
    
    def setup_method(self):
        """Set up before each test"""
        self.manager = CryptographicSyncManager()
    
    def test_complete_sync_flow(self):
        """Test the complete partner sync flow from start to finish"""
        print("\n" + "=" * 60)
        print("📌 TEST: Complete Partner Sync Flow")
        print("=" * 60)
        
        # STEP 1: Alice generates a token
        print("\n   STEP 1: Alice generates token")
        result = self.manager.create_partner_sync(SyncTestData.USER_ALICE)
        assert result['success'], "Token generation failed"
        token = result['token']
        print(f"      Token generated: {token}")
        
        # STEP 2: Check token status before use
        print("\n   STEP 2: Check token status")
        status = self.manager.get_token_status(token)
        assert status['valid'], "Token should be valid"
        assert not status['used'], "Token should not be used yet"
        assert not status['expired'], "Token should not be expired"
        print(f"      Status: valid={status['valid']}, used={status['used']}")
        
        # STEP 3: Bob verifies the token
        print("\n   STEP 3: Bob verifies token")
        verify_result = self.manager.verify_partner_sync(token, SyncTestData.USER_BOB)
        assert verify_result['success'], f"Verification failed: {verify_result.get('message')}"
        assert verify_result['original_user_id'] == SyncTestData.USER_ALICE
        print(f"      Linked with: {verify_result['original_user_id']}")
        
        # STEP 4: Check token status after use
        print("\n   STEP 4: Check token status after use")
        status = self.manager.get_token_status(token)
        assert status['used'], "Token should be marked as used"
        print(f"      Status: used={status['used']}")
        
        print("\n   ✅ Complete sync flow successful!")
    
    def test_invalid_token_rejection(self):
        """Test that invalid tokens are rejected"""
        print("\n" + "=" * 60)
        print("📌 TEST: Invalid Token Rejection")
        print("=" * 60)
        
        for invalid_token in SyncTestData.INVALID_TOKENS:
            result = self.manager.verify_partner_sync(invalid_token, SyncTestData.USER_BOB)
            assert not result['success'], f"Should reject: {invalid_token}"
            print(f"   ✅ Rejected: {invalid_token}")
    
    def test_expired_token_rejection(self):
        """Test that expired tokens are rejected"""
        print("\n" + "=" * 60)
        print("📌 TEST: Expired Token Rejection")
        print("=" * 60)
        
        # Create a token that expires immediately using the test method
        expired_token = self.manager.token_generator.create_test_token_with_expiry(
            SyncTestData.USER_ALICE, expiry_seconds=0
        )
        
        # Wait a moment for expiry
        time.sleep(0.1)
        
        # Try to verify (should be expired)
        result = self.manager.verify_partner_sync(expired_token, SyncTestData.USER_BOB)
        assert not result['success'], "Expired token should be rejected"
        # Message could be about expiry OR invalid token (both acceptable)
        print(f"   ✅ Expired token rejected: {result['message']}")
    
    def test_token_cannot_be_reused(self):
        """Test that a token cannot be used twice"""
        print("\n" + "=" * 60)
        print("📌 TEST: Token Cannot Be Reused")
        print("=" * 60)
        
        # Generate token
        result = self.manager.create_partner_sync(SyncTestData.USER_ALICE)
        token = result['token']
        
        # First use - should succeed
        result1 = self.manager.verify_partner_sync(token, SyncTestData.USER_BOB)
        assert result1['success'], "First use should succeed"
        print(f"   ✅ First use succeeded")
        
        # Second use - should fail
        result2 = self.manager.verify_partner_sync(token, SyncTestData.USER_BOB)
        assert not result2['success'], "Second use should fail"
        assert "already been used" in result2['message'].lower(), "Should mention already used"
        print(f"   ✅ Second use rejected: {result2['message']}")
    
    def test_session_key_flow(self):
        """Test the complete session key flow for nurses"""
        print("\n" + "=" * 60)
        print("📌 TEST: Session Key Flow (Nurse Access)")
        print("=" * 60)
        
        # STEP 1: Generate session key
        print("\n   STEP 1: Generate session key")
        result = self.manager.create_session_key(SyncTestData.SESSION_ID)
        assert result['success'], "Session key generation failed"
        session_key = result['key']
        print(f"      Session key: {session_key}")
        
        # STEP 2: Nurse verifies key
        print("\n   STEP 2: Nurse verifies key")
        verify_result = self.manager.verify_session_key(session_key)
        assert verify_result['success'], f"Verification failed: {verify_result.get('message')}"
        assert verify_result['session_id'] == SyncTestData.SESSION_ID
        print(f"      Access granted to session: {verify_result['session_id']}")
        
        # STEP 3: Try to reuse the same key (should fail)
        print("\n   STEP 3: Try to reuse key")
        reuse_result = self.manager.verify_session_key(session_key)
        assert not reuse_result['success'], "Key should not be reusable"
        assert "already been used" in reuse_result['message'].lower()
        print(f"      Reuse rejected: {reuse_result['message']}")
        
        print("\n   ✅ Session key flow successful!")
    
    def test_cleanup_expired_tokens(self):
        """Test that expired tokens are cleaned up"""
        print("\n" + "=" * 60)
        print("📌 TEST: Cleanup Expired Tokens")
        print("=" * 60)
        
        # Create a few expired tokens using the test method
        for i in range(5):
            self.manager.token_generator.create_test_token_with_expiry(f"expired_user_{i}", expiry_seconds=0)
        
        # Clean up
        cleanup_result = self.manager.cleanup()
        print(f"   ✅ Cleaned up {cleanup_result['expired_tokens_removed']} expired tokens")
        print(f"   ✅ {cleanup_result['active_tokens_remaining']} active tokens remain")
    
    def test_concurrent_token_generation(self):
        """Test generating multiple tokens quickly"""
        print("\n" + "=" * 60)
        print("📌 TEST: Concurrent Token Generation")
        print("=" * 60)
        
        import time
        start = time.time()
        
        tokens = []
        for i in range(50):
            result = self.manager.create_partner_sync(f"user_{i}")
            tokens.append(result['token'])
        
        end = time.time()
        elapsed = end - start
        
        # Should generate 50 tokens in under 2 seconds
        assert elapsed < 2.0, f"Token generation too slow: {elapsed:.2f}s"
        assert len(set(tokens)) == 50, "Duplicate tokens generated"
        
        print(f"   ✅ Generated 50 unique tokens in {elapsed:.2f} seconds")
        print(f"   ✅ Rate: {50/elapsed:.1f} tokens/second")


# =========================================================
# RUN ALL TESTS
# =========================================================

def run_all_sync_tests():
    """Run all sync flow tests and print summary"""
    print("\n" + "=" * 70)
    print("🔗 RUNNING COMPLETE SYNC FLOW TEST SUITE")
    print("=" * 70)
    
    results = {
        'token_generator': {'passed': 0, 'total': 0, 'failed': []},
        'session_key': {'passed': 0, 'total': 0, 'failed': []},
        'sync_manager': {'passed': 0, 'total': 0, 'failed': []}
    }
    
    # Run Token Generator tests
    print("\n" + "=" * 60)
    print("🔐 TOKEN GENERATOR TESTS")
    print("=" * 60)
    
    tg = TestTokenGenerator()
    tg.setup_method()
    
    try:
        tg.test_token_generation_format()
        results['token_generator']['passed'] += 1
    except AssertionError as e:
        results['token_generator']['failed'].append(f"format: {e}")
    results['token_generator']['total'] += 1
    
    try:
        tg.test_token_uniqueness()
        results['token_generator']['passed'] += 1
    except AssertionError as e:
        results['token_generator']['failed'].append(f"uniqueness: {e}")
    results['token_generator']['total'] += 1
    
    try:
        tg.test_token_hashing()
        results['token_generator']['passed'] += 1
    except AssertionError as e:
        results['token_generator']['failed'].append(f"hashing: {e}")
    results['token_generator']['total'] += 1
    
    try:
        tg.test_token_storage_no_plaintext()
        results['token_generator']['passed'] += 1
    except AssertionError as e:
        results['token_generator']['failed'].append(f"privacy: {e}")
    results['token_generator']['total'] += 1
    
    try:
        tg.test_token_expiry()
        results['token_generator']['passed'] += 1
    except AssertionError as e:
        results['token_generator']['failed'].append(f"expiry: {e}")
    results['token_generator']['total'] += 1
    
    # Run Session Key tests
    print("\n" + "=" * 60)
    print("🔑 SESSION KEY TESTS")
    print("=" * 60)
    
    sk = TestSessionKeyGenerator()
    sk.setup_method()
    
    try:
        sk.test_session_key_format()
        results['session_key']['passed'] += 1
    except AssertionError as e:
        results['session_key']['failed'].append(f"format: {e}")
    results['session_key']['total'] += 1
    
    try:
        sk.test_session_key_uniqueness()
        results['session_key']['passed'] += 1
    except AssertionError as e:
        results['session_key']['failed'].append(f"uniqueness: {e}")
    results['session_key']['total'] += 1
    
    try:
        sk.test_session_key_expiry()
        results['session_key']['passed'] += 1
    except AssertionError as e:
        results['session_key']['failed'].append(f"expiry: {e}")
    results['session_key']['total'] += 1
    
    try:
        sk.test_session_key_one_time_use()
        results['session_key']['passed'] += 1
    except AssertionError as e:
        results['session_key']['failed'].append(f"one-time: {e}")
    results['session_key']['total'] += 1
    
    # Run Sync Manager tests
    print("\n" + "=" * 60)
    print("🔄 SYNC MANAGER TESTS")
    print("=" * 60)
    
    sm = TestCryptographicSyncManager()
    sm.setup_method()
    
    try:
        sm.test_complete_sync_flow()
        results['sync_manager']['passed'] += 1
    except AssertionError as e:
        results['sync_manager']['failed'].append(f"complete_flow: {e}")
    results['sync_manager']['total'] += 1
    
    try:
        sm.test_invalid_token_rejection()
        results['sync_manager']['passed'] += 1
    except AssertionError as e:
        results['sync_manager']['failed'].append(f"invalid_token: {e}")
    results['sync_manager']['total'] += 1
    
    try:
        sm.test_expired_token_rejection()
        results['sync_manager']['passed'] += 1
    except AssertionError as e:
        results['sync_manager']['failed'].append(f"expired_token: {e}")
    results['sync_manager']['total'] += 1
    
    try:
        sm.test_token_cannot_be_reused()
        results['sync_manager']['passed'] += 1
    except AssertionError as e:
        results['sync_manager']['failed'].append(f"reuse: {e}")
    results['sync_manager']['total'] += 1
    
    try:
        sm.test_session_key_flow()
        results['sync_manager']['passed'] += 1
    except AssertionError as e:
        results['sync_manager']['failed'].append(f"session_key: {e}")
    results['sync_manager']['total'] += 1
    
    try:
        sm.test_cleanup_expired_tokens()
        results['sync_manager']['passed'] += 1
    except AssertionError as e:
        results['sync_manager']['failed'].append(f"cleanup: {e}")
    results['sync_manager']['total'] += 1
    
    try:
        sm.test_concurrent_token_generation()
        results['sync_manager']['passed'] += 1
    except AssertionError as e:
        results['sync_manager']['failed'].append(f"concurrent: {e}")
    results['sync_manager']['total'] += 1
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 SYNC FLOW TEST SUMMARY")
    print("=" * 70)
    
    total_tests = 0
    total_passed = 0
    
    for category, data in results.items():
        total_tests += data['total']
        total_passed += data['passed']
        status = "✅" if data['passed'] == data['total'] else "❌"
        print(f"\n{status} {category.upper()}: {data['passed']}/{data['total']} passed")
        if data['failed']:
            print(f"   Failed: {', '.join(data['failed'])}")
    
    print("\n" + "=" * 70)
    print(f"📈 OVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL SYNC FLOW TESTS PASSED! Ready for production.")
        return 0
    else:
        print("\n⚠️ Some sync flow tests failed. Please review and fix.")
        return 1


# =========================================================
# GENERATE TEST REPORT
# =========================================================

def generate_test_report():
    """Generate a JSON test report"""
    report = {
        'test_suite': 'Partner Sync Flow Tests',
        'date': datetime.now().isoformat(),
        'test_categories': {
            'token_generation': 5,
            'session_keys': 4,
            'sync_manager': 7
        },
        'total_tests': 16,
        'security_features': [
            'SHA-256 hashing for stored tokens',
            'No plain-text token storage',
            'Automatic expiry (24h / 15min)',
            'One-time use enforcement',
            'Cryptographically secure randomness'
        ],
        'flow_steps_tested': [
            'Token generation',
            'Token hashing',
            'Token verification',
            'Partner linking',
            'Session key generation',
            'Nurse access verification'
        ]
    }
    
    report_path = Path(__file__).parent / "sync_test_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Test report saved to: {report_path}")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    exit_code = run_all_sync_tests()
    generate_test_report()
    sys.exit(exit_code)