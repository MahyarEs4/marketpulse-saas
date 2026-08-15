from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    competitor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default="IRR")

    price: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    old_price: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    competitor = relationship("Competitor", backref="price_snapshots")
