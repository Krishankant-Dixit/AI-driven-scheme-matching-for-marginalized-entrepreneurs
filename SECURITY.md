# Security

Implemented controls include bcrypt password hashing, JWT signature/expiry validation, normalized unique emails, active-user checks, role-based admin dependencies, user-scoped resource queries, Pydantic validation, sanitized API errors, configurable CORS, and audit records for admin scheme/user changes.

Passwords, password hashes, tokens, authorization headers, and database credentials are not returned or logged. Rules are data only; arbitrary executable rule code is not accepted.

The MVP stores bearer tokens in localStorage for SPA compatibility. Production should migrate to secure HTTP-only cookies, add refresh-token rotation and revocation, enable HTTPS, add rate limiting, and provide monitoring/backups.
