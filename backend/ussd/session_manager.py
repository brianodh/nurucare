"""
NuruCare - USSD Session Manager
================================

Manages USSD sessions with support for:
- In-memory storage (for hackathon/development)
- Redis storage (for production)
- Automatic session expiry
- Progress tracking

Author: Brian Odhiambo Ouma
Date: July 2026
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Try to import Redis (optional)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


# ============================================
# IN-MEMORY SESSION STORAGE (Default)
# ============================================

class InMemorySessionStore:
    """
    Simple in-memory session storage for development.
    
    Sessions expire after 1 hour of inactivity.
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict] = {}
        self._expiry: Dict[str, datetime] = {}
        self._expiry_hours = 1
    
    def get(self, session_id: str) -> Optional[Dict]:
        """Get session data if not expired"""
        if session_id in self._expiry:
            if datetime.now() > self._expiry[session_id]:
                # Session expired
                self.delete(session_id)
                return None
        return self._sessions.get(session_id)
    
    def set(self, session_id: str, data: Dict, expiry_hours: int = 1):
        """Store session data with expiry"""
        self._sessions[session_id] = data
        self._expiry[session_id] = datetime.now() + timedelta(hours=expiry_hours)
    
    def delete(self, session_id: str):
        """Delete session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
        if session_id in self._expiry:
            del self._expiry[session_id]
    
    def update(self, session_id: str, data: Dict):
        """Update existing session"""
        if session_id in self._sessions:
            self._sessions[session_id].update(data)
            # Refresh expiry
            self._expiry[session_id] = datetime.now() + timedelta(hours=self._expiry_hours)
        else:
            self.set(session_id, data)
    
    def get_all(self) -> Dict:
        """Get all active sessions (for monitoring)"""
        # Clean expired sessions first
        expired = [sid for sid, exp in self._expiry.items() if datetime.now() > exp]
        for sid in expired:
            self.delete(sid)
        return self._sessions.copy()
    
    def count(self) -> int:
        """Get number of active sessions"""
        return len(self.get_all())


# ============================================
# REDIS SESSION STORAGE (Production)
# ============================================

class RedisSessionStore:
    """
    Redis-based session storage for production.
    
    Requires Redis server running.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, password: str = None):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis package not installed. Run: pip install redis")
        
        self.redis = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )
        self._prefix = "ussd:"
        self._expiry_hours = 1
    
    def get(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        key = f"{self._prefix}{session_id}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def set(self, session_id: str, data: Dict, expiry_hours: int = 1):
        """Store session data with expiry"""
        key = f"{self._prefix}{session_id}"
        self.redis.setex(
            key,
            expiry_hours * 3600,  # Convert hours to seconds
            json.dumps(data)
        )
    
    def delete(self, session_id: str):
        """Delete session"""
        key = f"{self._prefix}{session_id}"
        self.redis.delete(key)
    
    def update(self, session_id: str, data: Dict):
        """Update existing session"""
        key = f"{self._prefix}{session_id}"
        existing = self.get(session_id)
        if existing:
            existing.update(data)
            self.set(session_id, existing)
        else:
            self.set(session_id, data)
    
    def get_all(self) -> Dict:
        """Get all active sessions (for monitoring)"""
        keys = self.redis.keys(f"{self._prefix}*")
        result = {}
        for key in keys:
            session_id = key.replace(self._prefix, "")
            data = self.get(session_id)
            if data:
                result[session_id] = data
        return result
    
    def count(self) -> int:
        """Get number of active sessions"""
        return len(self.redis.keys(f"{self._prefix}*"))


# ============================================
# UNIFIED SESSION MANAGER
# ============================================

class USSDSessionManager:
    """
    Unified session manager with automatic storage selection.
    
    Uses:
    - Redis if available and configured
    - In-memory as fallback
    
    Environment variables:
    - REDIS_URL: Redis connection string
    - REDIS_HOST: Redis host (default: localhost)
    - REDIS_PORT: Redis port (default: 6379)
    - REDIS_PASSWORD: Redis password (optional)
    """
    
    def __init__(self):
        """Initialize session manager with best available storage"""
        self._store = None
        
        # Check if Redis is configured
        redis_url = os.getenv("REDIS_URL")
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT") or "6379")
        redis_password = os.getenv("REDIS_PASSWORD")
        
        # Try Redis first
        if REDIS_AVAILABLE and (redis_url or redis_host):
            try:
                if redis_url:
                    # Use Redis URL
                    import redis
                    self._store = redis.Redis.from_url(redis_url, decode_responses=True)
                else:
                    self._store = RedisSessionStore(redis_host, redis_port, redis_password)
                print("✅ Using Redis session storage")
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}")
                print("   Falling back to in-memory storage")
                self._store = InMemorySessionStore()
        else:
            print("✅ Using in-memory session storage")
            self._store = InMemorySessionStore()
        
        self._expiry_hours = int(os.getenv("SESSION_EXPIRY_HOURS") or "1")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get or create a session.
        
        Returns:
            Dict with 'step' and 'data' keys
        """
        data = self._store.get(session_id)
        if data is None:
            # Create new session
            data = {
                "step": 0,
                "data": {},
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "phone_number": None  # Will be set when available
            }
            self._store.set(session_id, data, self._expiry_hours)
        return data
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """
        Update session data (merge with existing).
        
        Args:
            session_id: Unique session identifier
            data: Data to update (will be merged)
        """
        # Get current session
        session = self.get_session(session_id)
        
        # Update data
        if "data" in data:
            session["data"].update(data["data"])
        else:
            session["data"].update(data)
        
        session["last_updated"] = datetime.now().isoformat()
        
        # Save back
        self._store.set(session_id, session, self._expiry_hours)
    
    def set_step(self, session_id: str, step: int):
        """Set current step"""
        session = self.get_session(session_id)
        session["step"] = step
        session["last_updated"] = datetime.now().isoformat()
        self._store.set(session_id, session, self._expiry_hours)
    
    def get_step(self, session_id: str) -> int:
        """Get current step"""
        return self.get_session(session_id).get("step", 0)
    
    def get_data(self, session_id: str) -> Dict[str, Any]:
        """Get all collected data"""
        return self.get_session(session_id).get("data", {})
    
    def delete_session(self, session_id: str):
        """Delete session when complete"""
        self._store.delete(session_id)
    
    def set_phone_number(self, session_id: str, phone_number: str):
        """Set user's phone number"""
        session = self.get_session(session_id)
        session["phone_number"] = phone_number
        self._store.set(session_id, session, self._expiry_hours)
    
    def get_phone_number(self, session_id: str) -> Optional[str]:
        """Get user's phone number"""
        return self.get_session(session_id).get("phone_number")
    
    def is_session_expired(self, session_id: str) -> bool:
        """Check if session is expired"""
        session = self.get_session(session_id)
        if "last_updated" in session:
            last_updated = datetime.fromisoformat(session["last_updated"])
            return datetime.now() > last_updated + timedelta(hours=self._expiry_hours)
        return False
    
    def count_active_sessions(self) -> int:
        """Get number of active sessions"""
        return self._store.count()
    
    def get_all_sessions(self) -> Dict:
        """Get all active sessions (for monitoring)"""
        return self._store.get_all()
    
    def cleanup_expired(self) -> int:
        """Clean up expired sessions"""
        # This is automatically handled by the store, but we provide a method
        # for manual cleanup if needed
        before = self._store.count()
        self._store.get_all()  # Triggers cleanup in InMemoryStore
        after = self._store.count()
        return before - after


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

_session_manager = None

def get_session_manager() -> USSDSessionManager:
    """Get the global session manager instance (singleton)"""
    global _session_manager
    if _session_manager is None:
        _session_manager = USSDSessionManager()
    return _session_manager


# ============================================
# TEST THE SESSION MANAGER
# ============================================

def test_session_manager():
    """Test the session manager functionality"""
    print("\n" + "=" * 60)
    print("🧪 TESTING USSD SESSION MANAGER")
    print("=" * 60)
    
    # Create session manager
    manager = get_session_manager()
    print(f"\n✅ Session Manager initialized")
    print(f"   Storage type: {type(manager._store).__name__}")
    
    # Test 1: Create session
    print("\n📌 Test 1: Create Session")
    session_id = "test_session_123"
    session = manager.get_session(session_id)
    print(f"   Session ID: {session_id}")
    print(f"   Initial step: {session['step']}")
    print(f"   Data: {session['data']}")
    
    # Test 2: Update session
    print("\n📌 Test 2: Update Session")
    manager.update_session(session_id, {"data": {"age": 28, "smoking": False}})
    manager.set_step(session_id, 3)
    updated = manager.get_session(session_id)
    print(f"   Step: {updated['step']}")
    print(f"   Data: {updated['data']}")
    
    # Test 3: Get data
    print("\n📌 Test 3: Get Data")
    data = manager.get_data(session_id)
    print(f"   Age: {data.get('age')}")
    print(f"   Smoking: {data.get('smoking')}")
    
    # Test 4: Delete session
    print("\n📌 Test 4: Delete Session")
    manager.delete_session(session_id)
    deleted = manager.get_session(session_id)
    print(f"   Step after delete: {deleted['step']}")
    print(f"   Data after delete: {deleted['data']}")
    
    # Test 5: Active sessions count
    print("\n📌 Test 5: Active Sessions")
    count = manager.count_active_sessions()
    print(f"   Active sessions: {count}")
    
    print("\n" + "=" * 60)
    print("✅ Session Manager Tests Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_session_manager()