/**
 * AuthContext — global authentication state management.
 *
 * Provides: user, token, loading, login(), register(), logout()
 * Stores token in localStorage and auto-loads user on mount.
 * Injects Authorization header into the shared Axios client.
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { loginUser, registerUser, getCurrentUser } from '../api/auth';

const AuthContext = createContext(null);

const TOKEN_KEY = 'nutriwise_token';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true);

  // Set/clear the default Authorization header on the shared Axios client
  const syncAuthHeader = useCallback((t) => {
    if (t) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${t}`;
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
    }
  }, []);

  // On mount (or token change), try to load the current user
  useEffect(() => {
    async function loadUser() {
      if (!token) {
        setUser(null);
        setLoading(false);
        syncAuthHeader(null);
        return;
      }

      syncAuthHeader(token);
      try {
        const userData = await getCurrentUser(token);
        setUser(userData);
      } catch {
        // Token is invalid/expired — clear everything
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setUser(null);
        syncAuthHeader(null);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, [token, syncAuthHeader]);

  const login = async ({ email, password }) => {
    const data = await loginUser({ email, password });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    syncAuthHeader(data.access_token);

    const userData = await getCurrentUser(data.access_token);
    setUser(userData);
    return userData;
  };

  const register = async ({ name, email, username, password }) => {
    const userData = await registerUser({ name, email, username, password });
    return userData;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    syncAuthHeader(null);
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
