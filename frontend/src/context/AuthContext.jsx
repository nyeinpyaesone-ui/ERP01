import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import api from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [currency, setCurrency] = useState("MMK");
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    sessionStorage.removeItem("erp.access");
    sessionStorage.removeItem("erp.refresh");
    setUser(null);
  }, []);

  const loadCurrency = useCallback(async () => {
    try {
      const { data } = await api.get("/business-profile/");
      setCurrency(data.currency || "MMK");
    } catch {
      setCurrency("MMK");
    }
  }, []);

  const loadUser = useCallback(async () => {
    const access = sessionStorage.getItem("erp.access");
    if (!access) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const { data } = await api.get("/auth/me/");
      setUser(data);
      await loadCurrency();
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  }, [logout, loadCurrency]);

  useEffect(() => {
    loadUser();
    const onUnauthorized = () => logout();
    window.addEventListener("erp:unauthorized", onUnauthorized);
    return () => window.removeEventListener("erp:unauthorized", onUnauthorized);
  }, [loadUser, logout]);

  const login = useCallback(async (username, password) => {
    try {
      const { data } = await api.post("/auth/token/", { username, password });
      sessionStorage.setItem("erp.access", data.access);
      sessionStorage.setItem("erp.refresh", data.refresh);
      const profile = await api.get("/auth/me/");
      setUser(profile.data);
      await loadCurrency();
      return profile.data;
    } catch (error) {
      sessionStorage.removeItem("erp.access");
      sessionStorage.removeItem("erp.refresh");
      setUser(null);
      throw error;
    }
  }, [loadCurrency]);

  const value = useMemo(
    () => ({ user, currency, loading, login, logout, refreshUser: loadUser }),
    [user, currency, loading, login, logout, loadUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
