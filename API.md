# API Overview

Authentication: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`.

Owned profile: `POST /api/profile`, `GET /api/profile/{profile_id}`.

Evaluation: `POST /api/eligibility/check`, `POST /api/matching/score`.

Recommendations: `POST /api/recommendations`, `GET /api/recommendations/history`, `GET /api/recommendations/history/{history_id}`, `DELETE /api/recommendations/history/{history_id}`.

Saved schemes: `GET /api/saved-schemes`, `POST /api/saved-schemes`, `DELETE /api/saved-schemes/{scheme_id}`.

Scheme details: `GET /api/schemes/{scheme_id}`.

Admin: `GET /api/admin/dashboard`, `GET/POST /api/admin/schemes`, `GET/PUT/DELETE /api/admin/schemes/{scheme_id}`, `PATCH /api/admin/schemes/{scheme_id}/status`, `GET /api/admin/users`, `PATCH /api/admin/users/{user_id}/status`, and `GET /api/admin/data-quality`.

All except public registration/login, health, and scheme details require a bearer token. Admin endpoints additionally require `role=ADMIN`.
