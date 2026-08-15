from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PriceChangeBase(BaseModel):
    competitor_id: int = Field(..., gt=0)
    current_snapshot_id: int = Field(..., gt=0)
    previous_snapshot_id: int | None = Field(default=None, gt=0)

    old_price: Decimal
    new_price: Decimal
    change_amount: Decimal
    change_percent: Decimal | None = None

    currency: str = "IRR"
    change_type: str
    notes: str | None = None
    detected_at: datetime


class PriceChangeCreate(PriceChangeBase):
    pass


class PriceChangeUpdate(BaseModel):
    competitor_id: int | None = Field(default=None, gt=0)
    current_snapshot_id: int | None = Field(default=None, gt=0)
    previous_snapshot_id: int | None = Field(default=None, gt=0)

    old_price: Decimal | None = None
    new_price: Decimal | None = None
    change_amount: Decimal | None = None
    change_percent: Decimal | None = None

    currency: str | None = None
    change_type: str | None = None
    notes: str | None = None
    detected_at: datetime | None = None


class PriceChangeOut(PriceChangeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
