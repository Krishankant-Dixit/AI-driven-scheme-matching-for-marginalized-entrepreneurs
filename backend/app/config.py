from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

MATCH_WEIGHTS = {
    "category": 20,
    "business": 30,
    "location": 10,
    "financial": 15,
    "business_stage": 10,
    "semantic": 15,
}
DETERMINISTIC_WEIGHT_TOTAL = sum(weight for name, weight in MATCH_WEIGHTS.items() if name != "semantic")
if DETERMINISTIC_WEIGHT_TOTAL != 85 or sum(MATCH_WEIGHTS.values()) != 100:
    raise ValueError("Matching weights must total 85 deterministic and 100 planned.")

RECOMMENDATION_THRESHOLDS = {
    "highly_recommended": 80,
    "recommended": 65,
    "potentially_relevant": 50,
}
DEFAULT_RECOMMENDATION_LIMIT = 10
MAX_RECOMMENDATION_LIMIT = 50


class Settings(BaseSettings):
    app_name: str = "SIH26092 Scheme Matching API"
    environment: str = "development"
    api_prefix: str = "/api"
    cors_origins: str = Field(default="http://localhost:5173")
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "sih26092"
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    admin_setup_secret: str | None = None
    frontend_url: str = "http://localhost:5173"
    semantic_model_name: str = ""
    recommendation_limit: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
