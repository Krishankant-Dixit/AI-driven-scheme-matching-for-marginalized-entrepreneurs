# Phase 9 Authentication and Ownership

The application uses bearer JWT authentication with bcrypt password hashing through `pwdlib`. The JWT secret, algorithm, and expiry are configured through environment variables. Passwords and password hashes are never returned to clients.

## Protected Resources

Profile creation/retrieval, eligibility checks, deterministic matching, recommendations, recommendation history, and saved schemes require an authenticated user. Profiles store `user_id`; every resource query includes the authenticated user's ID. A profile ID alone is never authorization.

Recommendation generation creates an immutable history snapshot containing the user and profile IDs, generated timestamp, recommendation summary, scheme versions, and model-version metadata. Saved schemes use a unique `(user_id, scheme_id)` index.

## Frontend Token Tradeoff

The MVP stores only the bearer token in `localStorage` through one API-client module so it can later migrate to HTTP-only cookies. This is convenient for the current SPA but has greater XSS exposure than secure HTTP-only cookies. Production deployment should use HTTPS, a strong `JWT_SECRET_KEY`, a restrictive configured CORS origin, and consider cookie-based sessions.

Logout clears the client token. JWTs remain valid until expiration because server-side revocation is not implemented in this phase.

Legacy profiles without `user_id` are not assigned automatically; they must be recreated or migrated explicitly by an administrator.

Rate limiting, email verification, password reset, refresh-token rotation, and server-side token revocation remain production hardening items.
