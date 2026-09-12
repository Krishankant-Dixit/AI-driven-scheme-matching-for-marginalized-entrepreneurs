# Architecture

The MVP is a React/Vite frontend backed by FastAPI, Pydantic, and MongoDB-compatible persistence.

```text
Auth -> owned business profile -> hard eligibility -> deterministic matching
     -> (semantic Phase 7 unavailable in this repository) -> recommendations
     -> history and saved schemes
```

Mandatory eligibility remains rule-driven. Match score and confidence are separate. Admin operations are role-protected and audit important changes. Scheme seed data remains in `data/`; admin-managed Mongo records are currently a management boundary and require a future synchronization decision before replacing seed data in evaluation.

## Modules

- `backend/app/core`: JWT/password security and admin authorization
- `backend/app/schemas`: Pydantic contracts
- `backend/app/services`: eligibility, matching, ranking, recommendation, profile services
- `backend/app/routes`: authenticated REST APIs
- `frontend/src`: auth-aware React pages and forms
