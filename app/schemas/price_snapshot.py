from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PriceSnapshotBase(BaseModel):
    competitor_id: int = Field(..., gt=0)
    source_url: str | None = None
    title: str | None = None
    currency: str = "IRR"
    price: Decimal
    old_price: Decimal | None = None
    notes: str | None = None
    captured_at: datetime | None = None


class PriceSnapshotCreate(PriceSnapshotBase):
    pass


class PriceSnapshotUpdate(BaseModel):
    source_url: str | None = None
    title: str | None = None
    currency: str | None = None
    price: Decimal | None = None
    old_price: Decimal | None = None
    notes: str | None = None
    captured_at: datetime | None = None


class PriceSnapshotOut(PriceSnapshotBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
