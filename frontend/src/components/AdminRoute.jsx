import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function AdminRoute() {
  const { loading, user } = useAuth();
  if (loading) return <main className="page-shell"><h1>Checking your session...</h1></main>;
  if (!user) return <Navigate to="/login" replace />;
  return user.role === "ADMIN" ? <Outlet /> : <main className="profile-shell"><h1>Administrator access required.</h1></main>;
}
