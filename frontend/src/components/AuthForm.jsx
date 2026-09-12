import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function AuthForm({ mode }) {
  const isRegister = mode === "register";
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    if (isRegister && form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      if (isRegister) await register(form.name, form.email, form.password);
      else await login(form.email, form.password);
      navigate(new URLSearchParams(location.search).get("next") || "/profile", { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to complete authentication.");
    } finally {
      setLoading(false);
    }
  }

  return <main className="auth-shell"><div className="auth-panel"><p className="eyebrow">SCHEMEMATCH</p><h1>{isRegister ? "Create your account" : "Welcome back"}</h1><p className="intro">Your account keeps your business profile and recommendations private.</p><form onSubmit={submit} className="auth-form">
    {isRegister && <label className="form-field" htmlFor="name"><span>Name</span><input id="name" required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>}
    <label className="form-field" htmlFor="email"><span>Email</span><input id="email" type="email" required value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label>
    <label className="form-field" htmlFor="password"><span>Password</span><input id="password" type="password" minLength="8" required value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>
    {isRegister && <label className="form-field" htmlFor="confirm"><span>Confirm password</span><input id="confirm" type="password" minLength="8" required value={form.confirm} onChange={(event) => setForm({ ...form, confirm: event.target.value })} /></label>}
    {error && <p className="form-status error">{error}</p>}<button className="primary-button" disabled={loading}>{loading ? "Please wait..." : isRegister ? "Create account" : "Log in"}</button>
  </form><p className="auth-switch">{isRegister ? "Already have an account?" : "Need an account?"} <Link className="text-link" to={isRegister ? "/login" : "/register"}>{isRegister ? "Log in" : "Register"}</Link></p></div></main>;
}