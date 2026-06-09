import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

// ─── Helpers ──────────────────────────────────────────────────────────────────
const STORAGE_KEY = 'nurucare_patient';

const loadStoredUser = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

const persistUser = (user) => {
  if (user) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
};

// ─── Provider ─────────────────────────────────────────────────────────────────
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);
  const [isLoadingPublicSettings, setIsLoadingPublicSettings] = useState(false);
  const [authError, setAuthError] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [appPublicSettings, setAppPublicSettings] = useState({ id: 'nurucare-app' });

  // Rehydrate session from localStorage on mount
  useEffect(() => {
    const stored = loadStoredUser();
    if (stored) {
      setUser(stored);
      setIsAuthenticated(true);
    }
    setIsLoadingAuth(false);
    setAuthChecked(true);
  }, []);

  // ── Sign Up ────────────────────────────────────────────────────────────────
  // consentGiven must be true before this is called (enforced by ConsentModal in SignUp.jsx)
  const signUp = async ({ name, email, password, consentGiven }) => {
    if (!consentGiven) {
      throw new Error('You must accept the data consent policy to create an account.');
    }

    // TODO: swap this block for a real API call when the backend is ready:
    // const res = await apiClient.post('/api/v1/auth/register', { name, email, password, consent: true });
    // const newUser = res.data;

    // Mock — creates a local patient record
    const newUser = {
      id: `usr_${Date.now()}`,
      name,
      email,
      role: 'patient',
      consentGiven: true,
      consentDate: new Date().toISOString(),
    };

    persistUser(newUser);
    setUser(newUser);
    setIsAuthenticated(true);
    return newUser;
  };

  // ── Login ──────────────────────────────────────────────────────────────────
  const login = async ({ email, password }) => {
    // TODO: replace with real API call:
    // const res = await apiClient.post('/api/v1/auth/login', { email, password });
    // const loggedInUser = res.data;

    // Mock — checks localStorage for a matching patient
    const stored = loadStoredUser();
    if (!stored || stored.email !== email) {
      throw new Error('No account found with that email. Please sign up first.');
    }
    // In production the backend verifies the password hash — skip here.

    setUser(stored);
    setIsAuthenticated(true);
    return stored;
  };

  // ── Logout ─────────────────────────────────────────────────────────────────
  const logout = async () => {
    // Optional: await apiClient.post('/api/v1/auth/logout');
    persistUser(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const navigateToLogin = () => {
    window.location.href = '/login';
  };

  const checkUserAuth = async () => {};
  const checkAppState = async () => {};

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoadingAuth,
        isLoadingPublicSettings,
        authError,
        appPublicSettings,
        authChecked,
        signUp,
        login,
        logout,
        navigateToLogin,
        checkUserAuth,
        checkAppState,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
