import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  headers: {
    "Content-Type": "application/json",
  },
});

export function getToken() {
  return window.localStorage.getItem("sih26092_access_token");
}

export function setToken(token) {
  window.localStorage.setItem("sih26092_access_token", token);
}

export function clearToken() {
  window.localStorage.removeItem("sih26092_access_token");
}

apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
