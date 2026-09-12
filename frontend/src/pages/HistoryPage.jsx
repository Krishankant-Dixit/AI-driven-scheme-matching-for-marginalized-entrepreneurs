import { useEffect, useState } from "react";

import { apiClient } from "../services/api";

export default function HistoryPage() {
  const [state, setState] = useState({ loading: true, items: [], error: "" });
  useEffect(() => { apiClient.get("/api/recommendations/history").then(({ data }) => setState({ loading: false, items: data, error: "" })).catch(() => setState({ loading: false, items: [], error: "Unable to load history." })); }, []);
  return <main className="profile-shell"><div className="profile-heading"><p className="eyebrow">HISTORY</p><h1>Recommendation history.</h1></div>{state.loading ? <p className="intro">Loading history...</p> : state.error ? <p className="form-status error">{state.error}</p> : state.items.length ? <div className="recommendation-list">{state.items.map((item) => <article className="recommendation-card" key={item._id}><h2>{new Date(item.generated_at).toLocaleString()}</h2><p>{item.summary.recommended} recommendations from {item.summary.evaluated} schemes.</p></article>)}</div> : <p className="empty-state">No recommendation history yet.</p>}</main>;
}