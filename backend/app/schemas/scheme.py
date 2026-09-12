from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas.common import SourceType, VerificationStatus


class SchemeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scheme_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    short_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    ministry: str | None = None
    department: str | None = None
    scheme_type: str | None = None
    target_beneficiaries: list[str] = Field(default_factory=list)
    supported_categories: list[str] = Field(default_factory=list)
    supported_genders: list[str] = Field(default_factory=list)
    supported_locations: list[str] = Field(default_factory=list)
    rural_urban: list[str] = Field(default_factory=list)
    business_stages: list[str] = Field(default_factory=list)
    business_types: list[str] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)
    age_rule: dict[str, Any] | None = None
    income_rule: dict[str, Any] | None = None
    investment_rule: dict[str, Any] | None = None
    loan_rule: dict[str, Any] | None = None
    enterprise_rule: dict[str, Any] | None = None
    mandatory_requirements: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    documents_required: list[str] = Field(default_factory=list)
    application_method: list[str] = Field(default_factory=list)
    official_source: str = Field(min_length=1)
    official_source_url: HttpUrl
    source_type: SourceType
    last_verified: date
    version: str = Field(min_length=1)
    active: bool
    notes: str | None = None


class SchemeSeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemes: list[SchemeRecord]


class RuleSeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules: list["SchemeRule"]


from app.schemas.rule import SchemeRule

RuleSeed.model_rebuild()
