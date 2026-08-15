from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class CompetitorBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    website: HttpUrl | None = None
    phone: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    is_active: bool = True


class CompetitorCreate(CompetitorBase):
    pass


class CompetitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    website: HttpUrl | None = None
    phone: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    is_active: bool | None = None


class CompetitorOut(CompetitorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
