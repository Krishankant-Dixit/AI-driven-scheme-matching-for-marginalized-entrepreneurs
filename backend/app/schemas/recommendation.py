from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas.eligibility import ConfidenceLevel, EligibilityDecision


class RecommendationCategory(StrEnum):
    HIGHLY_RECOMMENDED = "HIGHLY_RECOMMENDED"
    RECOMMENDED = "RECOMMENDED"
    POTENTIALLY_RELEVANT = "POTENTIALLY_RELEVANT"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    NOT_RECOMMENDED = "NOT_RECOMMENDED"


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str = Field(min_length=1)


class RecommendationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int | None = None
    scheme_id: str
    scheme_name: str
    eligibility_status: EligibilityDecision
    recommendation_category: RecommendationCategory
    final_match_score: float | None = None
    deterministic_match_score: float | None = None
    semantic_score: float | None = None
    confidence: ConfidenceLevel
    score_breakdown: dict[str, float | None]
    explanations: list[str]
    verification_required: bool
    missing_information: list[str]
    official_source: str
    official_source_url: HttpUrl
    source_type: str
    last_verified: str
    version: str
    ranking_score: float | None = None


class RecommendationSummary(BaseModel):
    evaluated: int
    eligible: int
    needs_verification: int
    not_eligible: int
    recommended: int


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    profile_id: str
    generated_at: datetime
    total_schemes_evaluated: int
    total_recommendations: int
    summary: RecommendationSummary
    recommendations: list[RecommendationItem]
    excluded: list[RecommendationItem] = Field(default_factory=list)