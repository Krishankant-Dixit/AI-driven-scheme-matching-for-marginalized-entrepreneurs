# Production Notes

## Implemented

- JWT authentication and bcrypt password hashing
- USER/ADMIN roles and protected admin APIs
- Profile, recommendation, history, and saved-scheme ownership
- Configurable CORS and environment-based secrets
- Scheme data validation through Pydantic
- Health endpoint with degraded database status
- Backend test suite and frontend production build

## Recommended before public launch

- Run integration tests against a dedicated MongoDB Atlas test database.
- Migrate bearer tokens from localStorage to HTTP-only secure cookies.
- Add login/registration/recommendation rate limiting.
- Add password reset, email verification, refresh-token rotation, revocation, monitoring, backups, and alerting.
- Resolve synchronization between admin-managed Mongo scheme records and JSON seed data.
- Implement and deploy the missing Phase 7 semantic matching service before claiming AI-powered final scores.
- Add browser-level frontend tests and accessibility audits.
