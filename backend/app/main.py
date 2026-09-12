from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.eligibility import router as eligibility_router
from app.routes.auth import router as auth_router
from app.routes.matching import router as matching_router
from app.routes.profile import router as profile_router
from app.routes.recommendation import router as recommendation_router
from app.routes.history import router as history_router
from app.routes.saved_schemes import router as saved_schemes_router
from app.routes.admin import router as admin_router
from app.routes.schemes import router as schemes_router

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(eligibility_router, prefix=settings.api_prefix)
app.include_router(matching_router, prefix=settings.api_prefix)
app.include_router(recommendation_router, prefix=settings.api_prefix)
app.include_router(history_router, prefix=settings.api_prefix)
app.include_router(saved_schemes_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)
app.include_router(schemes_router, prefix=settings.api_prefix)


@app.get(f"{settings.api_prefix}/health", tags=["system"])
def health_check() -> dict[str, str]:
    try:
        from app.database.mongodb import get_database
        get_database().command("ping")
        database_status = "connected"
    except Exception:
        database_status = "unavailable"
    return {"status": "ok" if database_status == "connected" else "degraded", "service": "backend", "database": database_status}
