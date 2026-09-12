import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiClient } from "../services/api";

export default function SchemeDetailsPage() {
  const { schemeId } = useParams();
  const [state, setState] = useState({ loading: true, data: null, error: "" });
  useEffect(() => { apiClient.get(`/api/schemes/${encodeURIComponent(schemeId)}`).then(({ data }) => setState({ loading: false, data, error: "" })).catch(() => setState({ loading: false, data: null, error: "Scheme details are unavailable." })); }, [schemeId]);
  if (state.loading) return <main className="profile-shell"><h1>Loading scheme...</h1></main>;
  if (state.error) return <main className="profile-shell"><p className="form-status error">{state.error}</p></main>;
  const scheme = state.data;
  return <main className="profile-shell"><div className="profile-heading"><Link className="text-link" to="/recommendations">Back to recommendations</Link><p className="eyebrow">SCHEME DETAILS</p><h1>{scheme.name}</h1><p className="intro">{scheme.description}</p></div><article className="recommendation-card scheme-detail"><p><strong>Source:</strong> {scheme.official_source}</p><p><strong>Last verified:</strong> {scheme.last_verified}</p><p><strong>Version:</strong> {scheme.version}</p><h2>Benefits</h2><ul className="reason-list">{scheme.benefits.map((benefit) => <li key={benefit}>{benefit}</li>)}</ul><a className="source-link" href={scheme.official_source_url} target="_blank" rel="noreferrer">Open official source</a></article></main>;
}
