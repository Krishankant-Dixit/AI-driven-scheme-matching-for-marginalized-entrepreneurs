from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas.common import SourceType, VerificationStatus


class RuleType(StrEnum):
    AGE = "AGE"
    GENDER = "GENDER"
    CATEGORY = "CATEGORY"
    LOCATION = "LOCATION"
    RURAL_URBAN = "RURAL_URBAN"
    BUSINESS_TYPE = "BUSINESS_TYPE"
    BUSINESS_SECTOR = "BUSINESS_SECTOR"
    BUSINESS_STAGE = "BUSINESS_STAGE"
    NEW_ENTERPRISE = "NEW_ENTERPRISE"
    EXISTING_BUSINESS = "EXISTING_BUSINESS"
    INCOME = "INCOME"
    INVESTMENT = "INVESTMENT"
    LOAN_REQUIREMENT = "LOAN_REQUIREMENT"
    REQUIRED_INFORMATION = "REQUIRED_INFORMATION"
    CUSTOM = "CUSTOM"


class RuleOperator(StrEnum):
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    GREATER_THAN = "GREATER_THAN"
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"
    LESS_THAN = "LESS_THAN"
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"
    IN = "IN"
    NOT_IN = "NOT_IN"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    BETWEEN = "BETWEEN"
    ANY_OF = "ANY_OF"
    ALL_OF = "ALL_OF"
    EXISTS = "EXISTS"
    REQUIRED = "REQUIRED"
    CUSTOM = "CUSTOM"


class SchemeRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(min_length=1)
    scheme_id: str = Field(min_length=1)
    rule_type: RuleType
    field: str = Field(min_length=1)
    operator: RuleOperator
    expected_value: Any = None
    mandatory: bool
    source: str = Field(min_length=1)
    verification_status: VerificationStatus
    source_type: SourceType
    notes: str | None = None
