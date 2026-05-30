import React, { createContext, useState, useContext, useEffect } from 'react';
import { apiClient } from '@/api/apiClient';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({
    id: "usr_mock_nuru_99",
    name: "Dr. Alex Nuru",
    email: "provider@nurucare.org",
    role: "nurse", // 💡 Tip: Swap to "patient" to test your intake forms/client views
    avatar: "https://unsplash.com"
  });
  
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [isLoadingAuth, setIsLoadingAuth] = useState(false);
  const [isLoadingPublicSettings, setIsLoadingPublicSettings] = useState(false);
  const [authError, setAuthError] = useState(null);
  const [authChecked, setAuthChecked] = useState(true);
  const [appPublicSettings, setAppPublicSettings] = useState({ id: "demo-app" });

  // 🐍 FASTAPI BACKEND INTEGRATION READY
  // When your partner finishes the FastAPI auth endpoints, uncomment this block:
  /*
  useEffect(() => {
    const fetchUserSession = async () => {
      try {
        setIsLoadingAuth(true);
        const response = await apiClient.get('/api/v1/auth/me');
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (error) {
        console.error("No active session found:", error);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setIsLoadingAuth(false);
        setAuthChecked(true);
      }
    };
    fetchUserSession();
  }, []);
  */

  const logout = async () => {
    try {
      // Optional: await apiClient.post('/api/v1/auth/logout');
    } catch (e) {
      console.error(e);
    }
    setUser(null);
    setIsAuthenticated(false);
    window.location.reload();
  };

  const navigateToLogin = () => {
    console.log("Redirecting to your custom login page route...");
  };

  const checkUserAuth = async () => {};
  const checkAppState = async () => {};

  return (
    <AuthContext.Provider value={{ 
      user, 
      isAuthenticated, 
      isLoadingAuth,
      isLoadingPublicSettings,
      authError,
      appPublicSettings,
      authChecked,
      logout,
      navigateToLogin,
      checkUserAuth,
      checkAppState
    }}>
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
