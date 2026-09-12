from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.eligibility import ConfidenceLevel, EligibilityDecision


class MatchDimensionStatus(StrEnum):
    MATCH = "MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    NO_MATCH = "NO_MATCH"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INVALID = "INVALID"


class MatchDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: str
    score: float | None = Field(default=None, ge=0, le=100)
    weight: int
    status: MatchDimensionStatus
    user_value: Any = None
    scheme_value: Any = None
    message: str


class MatchingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str | None = None
    scheme_id: str
    eligibility_status: EligibilityDecision
    eligible_for_matching: bool
    deterministic_match_score: float | None = Field(default=None, ge=0, le=100)
    semantic_score: None = None
    final_match_score: None = None
    dimensions: dict[str, MatchDimension]
    unknown_dimensions: list[str]
    not_applicable_dimensions: list[str]
    confidence: ConfidenceLevel
    explanations: list[str]