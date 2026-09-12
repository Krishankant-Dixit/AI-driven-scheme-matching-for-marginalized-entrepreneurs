import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { apiClient } from "../services/api";

function score(item) {
  return item.final_match_score ?? item.deterministic_match_score;
}

function RecommendationCard({ item }) {
  const [saveState, setSaveState] = useState("");
  const itemScore = score(item);
  async function saveScheme() {
    setSaveState("Saving...");
    try {
      await apiClient.post("/api/saved-schemes", { scheme_id: item.scheme_id });
      setSaveState("Saved");
    } catch (error) {
      setSaveState(error.response?.status === 409 ? "Already saved" : "Could not save");
    }
  }
  return (
    <article className="recommendation-card">
      <div className="recommendation-card-topline">
        <span className="rank-label">{item.rank ? `#${item.rank}` : "Review"}</span>
        <span className={`recommendation-badge ${item.recommendation_category.toLowerCase()}`}>{item.recommendation_category.replaceAll("_", " ")}</span>
      </div>
      <h2><Link className="text-link" to={`/schemes/${encodeURIComponent(item.scheme_id)}`}>{item.scheme_name}</Link></h2>
      <div className="recommendation-metrics">
        <div><strong>{itemScore === null ? "Not available" : `${itemScore.toFixed(1)}%`}</strong><span>Match score</span></div>
        <div><strong>{item.eligibility_status.replaceAll("_", " ")}</strong><span>Eligibility</span></div>
        <div><strong>{item.confidence}</strong><span>Confidence</span></div>
      </div>
      {itemScore !== null && <div className="score-track"><span style={{ width: `${itemScore}%` }} /></div>}
      <ul className="reason-list">
        {item.explanations.slice(0, 4).map((reason) => <li key={reason}>{reason}</li>)}
      </ul>
      {item.verification_required && <p className="verification-note">Eligibility needs verification before it can be confirmed.</p>}
      <a className="source-link" href={item.official_source_url} target="_blank" rel="noreferrer">Official source</a>
      <button className="secondary-button save-button" onClick={saveScheme} disabled={Boolean(saveState && saveState !== "Could not save")}>{saveState || "Save scheme"}</button>
    </article>
  );
}

export default function RecommendationsPage() {
  const [searchParams] = useSearchParams();
  const [filter, setFilter] = useState("ALL");
  const [state, setState] = useState({ loading: true, error: "", data: null });
  const profileId = searchParams.get("profile_id") || window.localStorage.getItem("sih26092_profile_id");

  useEffect(() => {
    if (!profileId) {
      setState({ loading: false, error: "Create a profile before viewing recommendations.", data: null });
      return;
    }
    apiClient.post("/api/recommendations", { profile_id: profileId })
      .then(({ data }) => setState({ loading: false, error: "", data }))
      .catch((error) => setState({ loading: false, error: error.response?.data?.detail || "Recommendations are temporarily unavailable.", data: null }));
  }, [profileId]);

  if (state.loading) return <main className="profile-shell"><p className="eyebrow">RECOMMENDATIONS</p><h1>Loading recommendations...</h1></main>;
  if (state.error) return <main className="profile-shell"><p className="eyebrow">RECOMMENDATIONS</p><h1>We could not load recommendations.</h1><p className="intro">{state.error}</p><Link className="text-link" to="/profile">Return to profile</Link></main>;

  const visible = state.data.recommendations.filter((item) => filter === "ALL" || (filter === "ELIGIBLE" ? item.eligibility_status === "ELIGIBLE" : item.eligibility_status === "NEEDS_VERIFICATION"));
  return (
    <main className="profile-shell recommendations-shell">
      <div className="profile-heading">
        <Link className="text-link" to="/profile">Edit profile</Link>
        <p className="eyebrow">PHASE 8 / RECOMMENDATIONS</p>
        <h1>Relevant schemes, clearly explained.</h1>
        <p className="intro">Scores describe profile relevance. They do not guarantee government approval or eligibility.</p>
      </div>
      <div className="recommendation-summary">
        <span><strong>{state.data.summary.evaluated}</strong> evaluated</span>
        <span><strong>{state.data.summary.eligible}</strong> eligible</span>
        <span><strong>{state.data.summary.needs_verification}</strong> need verification</span>
      </div>
      <div className="filter-row" role="group" aria-label="Recommendation filters">
        {["ALL", "ELIGIBLE", "NEEDS_VERIFICATION"].map((value) => <button key={value} className={filter === value ? "filter-button active" : "filter-button"} onClick={() => setFilter(value)}>{value.replaceAll("_", " ")}</button>)}
      </div>
      {visible.length ? <div className="recommendation-list">{visible.map((item) => <RecommendationCard key={item.scheme_id} item={item} />)}</div> : <p className="empty-state">No strongly matching schemes were found based on the information provided.</p>}
    </main>
  );
}
