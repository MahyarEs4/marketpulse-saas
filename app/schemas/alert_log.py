from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertLogBase(BaseModel):
    price_change_id: int
    channel: str = "telegram"
    status: str = "pending"
    message: str
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None


class AlertLogCreate(AlertLogBase):
    pass


class AlertLogUpdate(BaseModel):
    status: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None


class AlertLogOut(AlertLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
