from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"
    UNKNOWN = "UNKNOWN"


class Category(StrEnum):
    GENERAL = "GENERAL"
    SC = "SC"
    ST = "ST"
    OBC = "OBC"
    MINORITY = "MINORITY"
    WOMEN = "WOMEN"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class RuralUrban(StrEnum):
    RURAL = "RURAL"
    URBAN = "URBAN"
    UNKNOWN = "UNKNOWN"


class BusinessStage(StrEnum):
    IDEA = "IDEA"
    NEW = "NEW"
    EXISTING = "EXISTING"
    EXPANSION = "EXPANSION"
    UNKNOWN = "UNKNOWN"


class BusinessType(StrEnum):
    PROPRIETORSHIP = "PROPRIETORSHIP"
    PARTNERSHIP = "PARTNERSHIP"
    COMPANY = "COMPANY"
    SELF_HELP_GROUP = "SELF_HELP_GROUP"
    INDIVIDUAL = "INDIVIDUAL"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class BusinessSector(StrEnum):
    AGRICULTURE = "AGRICULTURE"
    FOOD_PROCESSING = "FOOD_PROCESSING"
    MANUFACTURING = "MANUFACTURING"
    SERVICES = "SERVICES"
    RETAIL = "RETAIL"
    HANDICRAFT = "HANDICRAFT"
    TEXTILE = "TEXTILE"
    TECHNOLOGY = "TECHNOLOGY"
    EDUCATION = "EDUCATION"
    HEALTHCARE = "HEALTHCARE"
    TOURISM = "TOURISM"
    TRANSPORT = "TRANSPORT"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class ProfileCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    age: int | None = Field(default=None, ge=1, le=120)
    gender: Gender | None = None
    category: Category | None = None
    state: str = Field(min_length=1, max_length=100)
    district: str = Field(min_length=1, max_length=100)
    rural_urban: RuralUrban | None = None
    business_name: str | None = Field(default=None, max_length=200)
    business_type: BusinessType | None = None
    business_sector: BusinessSector | None = None
    business_stage: BusinessStage | None = None
    business_description: str | None = Field(default=None, max_length=2000)
    annual_income: float | None = Field(default=None, ge=0)
    investment_capacity: float | None = Field(default=None, ge=0)
    loan_required: float | None = Field(default=None, ge=0)
    education: str | None = Field(default=None, max_length=200)
    disability_status: str | None = Field(default=None, max_length=100)
    social_category_details: str | None = Field(default=None, max_length=500)
    existing_business_duration: float | None = Field(default=None, ge=0)
    number_of_employees: int | None = Field(default=None, ge=0)

    @field_validator("name", "state", "district", mode="before")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("must not be blank")
        return value.strip()

    @field_validator(
        "business_name",
        "education",
        "disability_status",
        "social_category_details",
        "business_description",
        mode="before",
    )
    @classmethod
    def optional_text_is_trimmed(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        trimmed = value.strip()
        return trimmed or None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    profile_id: str
    profile: ProfileCreate
    created_at: datetime
    updated_at: datetime