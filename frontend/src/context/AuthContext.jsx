import { createContext, useContext, useEffect, useState } from "react";

import { apiClient, clearToken, getToken, setToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, setState] = useState({ loading: true, user: null });

  useEffect(() => {
    if (!getToken()) {
      setState({ loading: false, user: null });
      return;
    }
    apiClient.get("/api/auth/me")
      .then(({ data }) => setState({ loading: false, user: data }))
      .catch(() => {
        clearToken();
        setState({ loading: false, user: null });
      });
  }, []);

  async function login(email, password) {
    const { data } = await apiClient.post("/api/auth/login", { email, password });
    setToken(data.access_token);
    setState({ loading: false, user: data.user });
  }

  async function register(name, email, password) {
    await apiClient.post("/api/auth/register", { name, email, password });
    await login(email, password);
  }

  function logout() {
    clearToken();
    setState({ loading: false, user: null });
  }

  return <AuthContext.Provider value={{ ...state, isAuthenticated: Boolean(state.user), login, register, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
