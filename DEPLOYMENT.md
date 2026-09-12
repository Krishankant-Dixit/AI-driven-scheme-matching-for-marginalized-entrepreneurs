# Deployment

## Backend

Configure `MONGODB_URI`, `MONGODB_DATABASE`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`, and `ADMIN_SETUP_SECRET`. Install `backend/requirements.txt` and run:

```powershell
$env:PYTHONPATH="backend"
uvicorn app.main:app --host 0.0.0.0 --port $env:PORT
```

## Frontend

Set `VITE_API_BASE_URL` to the deployed backend URL, then run `npm install` and `npm run build` from `frontend/`. Deploy the generated `dist/` directory to a static host.

## MongoDB and CORS

Use MongoDB Atlas or a managed MongoDB instance. Never commit credentials. Set `CORS_ORIGINS` to comma-separated exact frontend origins; do not use wildcard origins with credentials.

## Semantic model

This repository does not currently contain the Phase 7 semantic service or model. `semantic_score` and `final_match_score` remain null; recommendation ranking uses the explicitly provisional deterministic score documented in `docs/recommendation-engine.md`.
