from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SavedSchemeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scheme_id: str = Field(min_length=1)


class SavedSchemeResponse(BaseModel):
    id: str
    scheme_id: str
    scheme_version: str
    saved_at: datetime
