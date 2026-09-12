from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ValueState
from app.schemas.rule import RuleType


class EligibilityDecision(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    INVALID = "INVALID"


class ConfidenceLevel(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RuleEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_type: RuleType
    field: str
    mandatory: bool
    status: ValueState
    user_value: Any = None
    expected_value: Any = None
    source: str
    source_type: str
    message: str


class EligibilitySummary(BaseModel):
    total_rules: int = Field(ge=0)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    unknown: int = Field(ge=0)
    not_applicable: int = Field(ge=0)
    invalid: int = Field(ge=0)


class EligibilityResult(BaseModel):
    scheme_id: str
    decision: EligibilityDecision
    confidence: ConfidenceLevel
    rules: list[RuleEvaluation]
    summary: EligibilitySummary
    verification_warnings: list[str] = Field(default_factory=list)


class EligibilityCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str = Field(min_length=1)
    scheme_id: str = Field(min_length=1)