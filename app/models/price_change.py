from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PriceChange(Base):
    __tablename__ = "price_changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    competitor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    current_snapshot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("price_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    previous_snapshot_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("price_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    old_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    new_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    change_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    change_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    currency: Mapped[str] = mapped_column(String(20), nullable=False, server_default="IRR")
    change_type: Mapped[str] = mapped_column(String(20), nullable=False)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # FIX: default اضافه شد تا INSERT بدون detected_at صریح هم کار کند
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    competitor = relationship("Competitor", backref="price_changes")
    current_snapshot = relationship("PriceSnapshot", foreign_keys=[current_snapshot_id])
    previous_snapshot = relationship("PriceSnapshot", foreign_keys=[previous_snapshot_id])

    alert_logs = relationship(
        "AlertLog",
        back_populates="price_change",
        cascade="all, delete-orphan",
    )
