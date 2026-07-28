import React, { createContext, useState, useContext, useEffect } from 'react';
import { nurseLogin, createPatientSession, getMe, signup as signupApi, login as loginApi } from '@/api/apiClient';

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

/**
 * Client-side JWT payload decode. For UX convenience only (self-action guard etc).
 * Backend always validates signatures properly; this never reads the secret.
 */
const decodeJwtPayload = (token) => {
  if (!token || typeof token !== 'string') return null;
  try {
    const parts = token.split('.');
    if (parts.length < 2) return null;
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(json);
  } catch {
    return null;
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

  // ── Nurse Login ─────────────────────────────────────────────────────────────
  const loginNurse = async ({ username, password }) => {
    const res = await nurseLogin(username, password);
    const jwt = decodeJwtPayload(res.access_token);
    const sub = jwt?.sub || username;
    const nurseUser = {
      id: sub,
      sub: sub,
      username: username,
      name: res.name,
      role: res.role,
      gender: res.gender,
      access_token: res.access_token,
      token_type: res.token_type,
    };
    persistUser(nurseUser);
    setUser(nurseUser);
    setIsAuthenticated(true);
    return nurseUser;
  };

  // ── Patient Session ─────────────────────────────────────────────────────────
  const loginPatient = async () => {
    const res = await createPatientSession();
    const jwt = decodeJwtPayload(res.access_token);
    const sub = jwt?.sub || res.profile_id;
    const patientUser = {
      id: sub,
      sub: sub,
      profile_id: res.profile_id,
      role: 'patient',
      access_token: res.access_token,
      token_type: res.token_type,
    };
    persistUser(patientUser);
    setUser(patientUser);
    setIsAuthenticated(true);
    return patientUser;
  };

  // ── Sign Up ────────────────────────────────────────────────────────────────
  const signUp = async ({ full_name, email, username, password, consentGiven, gender, role, institution_name, institution_address }) => {
    if (!consentGiven) {
      throw new Error('You must accept the data consent policy to create an account.');
    }
    const res = await signup({
      username,
      email,
      password,
      full_name,
      role,
      gender,
      institution_name,
      institution_address
    });
    const jwt = decodeJwtPayload(res.access_token);
    const sub = jwt?.sub || res.user_id;
    const newUser = {
      id: sub,
      sub: sub,
      username: username,
      email: email,
      name: full_name,
      role: res.role,
      gender: gender,
      access_token: res.access_token,
      token_type: 'bearer'
    };
    persistUser(newUser);
    setUser(newUser);
    setIsAuthenticated(true);
    return newUser;
  };

  // ── Login ──────────────────────────────────────────────────────────────────
  const login = async ({ username, password }) => {
    const res = await loginApi(username, password);
    const jwt = decodeJwtPayload(res.access_token);
    const sub = jwt?.sub || username;
    const loggedInUser = {
      id: sub,
      sub: sub,
      username: username,
      name: res.name,
      role: res.role,
      gender: res.gender,
      access_token: res.access_token,
      token_type: res.token_type
    };
    persistUser(loggedInUser);
    setUser(loggedInUser);
    setIsAuthenticated(true);
    return loggedInUser;
  };

  // ── Logout ─────────────────────────────────────────────────────────────────
  const logout = async () => {
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
        setUser,
        isAuthenticated,
        setIsAuthenticated,
        isLoadingAuth,
        isLoadingPublicSettings,
        authError,
        appPublicSettings,
        authChecked,
        signUp,
        login,
        loginNurse,
        loginPatient,
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
