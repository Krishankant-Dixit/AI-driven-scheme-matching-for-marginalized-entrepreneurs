# Phase 8 Recommendation Engine

The recommendation service evaluates active schemes by reusing the Phase 5 eligibility service and Phase 6 deterministic matching service. It does not introduce new eligibility rules or scheme-specific branches.

## Ranking

`NOT_ELIGIBLE` and invalid results are excluded from primary recommendations and retained in `excluded`. `NEEDS_VERIFICATION` results may appear, but remain clearly labeled and never claim confirmed eligibility. Eligible results are ranked by the available score, confidence, freshness, and stable `scheme_id`.

The repository currently has no Phase 7 semantic service. Therefore Phase 8 preserves `semantic_score` and `final_match_score` as `null` and uses the available deterministic score only as an explicitly provisional `ranking_score`. Once Phase 7 supplies semantic scores, the orchestration contract can calculate the final weighted score without changing the filtering or ranking boundaries.

Thresholds are centralized in `backend/app/config.py`: 80 for highly recommended, 65 for recommended, and 50 for potentially relevant. Threshold labels are recommendation categories, not government eligibility decisions.

## API

```http
POST /api/recommendations?limit=10
Content-Type: application/json

{"profile_id": "..."}
```

The frontend page is `/recommendations`. It reads the saved profile ID, displays loading/error/empty states, shows recommendation cards, and links to each official source.