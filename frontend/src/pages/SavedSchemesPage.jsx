import { useEffect, useState } from "react";

import { apiClient } from "../services/api";

export default function SavedSchemesPage() {
  const [items, setItems] = useState(null);
  useEffect(() => { apiClient.get("/api/saved-schemes").then(({ data }) => setItems(data)).catch(() => setItems([])); }, []);
  async function remove(schemeId) { await apiClient.delete(`/api/saved-schemes/${schemeId}`); setItems((current) => current.filter((item) => item.scheme_id !== schemeId)); }
  return <main className="profile-shell"><div className="profile-heading"><p className="eyebrow">SAVED SCHEMES</p><h1>Your saved schemes.</h1></div>{items === null ? <p className="intro">Loading saved schemes...</p> : items.length ? <div className="recommendation-list">{items.map((item) => <article className="recommendation-card" key={item.id}><h2>{item.scheme_id}</h2><p>Version {item.scheme_version}</p><button className="secondary-button" onClick={() => remove(item.scheme_id)}>Remove</button></article>)}</div> : <p className="empty-state">No saved schemes yet.</p>}</main>;
}