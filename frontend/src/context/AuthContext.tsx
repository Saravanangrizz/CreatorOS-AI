import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { api, setToken } from "../lib/api";

interface AuthContextValue {
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  loginDemo: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
    () => !!localStorage.getItem("creatoros_token")
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loginDemo = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { access_token } = await api.demoLogin();
      setToken(access_token);
      setIsAuthenticated(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reach the backend");
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setIsAuthenticated(false);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, loading, error, loginDemo, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
