import { useEffect, useState } from "react";

import { apiClient } from "../services/api";

export default function AdminPage() {
  const [state, setState] = useState({ loading: true, data: null, error: "" });
  useEffect(() => { apiClient.get("/api/admin/dashboard").then(({ data }) => setState({ loading: false, data, error: "" })).catch((error) => setState({ loading: false, data: null, error: error.response?.data?.detail || "Unable to load admin data." })); }, []);
  if (state.loading) return <main className="profile-shell"><h1>Loading admin dashboard...</h1></main>;
  if (state.error) return <main className="profile-shell"><p className="form-status error">{state.error}</p></main>;
  const { data } = state;
  return <main className="profile-shell"><div className="profile-heading"><p className="eyebrow">ADMINISTRATION</p><h1>Scheme operations.</h1><p className="intro">Manage verified scheme data and monitor data quality.</p></div><div className="recommendation-summary"><span><strong>{data.schemes.total}</strong> total schemes</span><span><strong>{data.schemes.active}</strong> active</span><span><strong>{data.users}</strong> users</span><span><strong>{data.recommendation_activity}</strong> history records</span></div><p className={data.data_quality_warnings.length ? "form-status error" : "form-status success"}>{data.data_quality_warnings.length ? `${data.data_quality_warnings.length} data quality warnings require review.` : "Data quality checks passed."}</p></main>;
}
