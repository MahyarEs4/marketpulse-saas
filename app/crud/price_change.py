from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_change import PriceChange
from app.schemas.price_change import PriceChangeCreate, PriceChangeUpdate


async def create_price_change(db: AsyncSession, change_in: PriceChangeCreate) -> PriceChange:
    change = PriceChange(**change_in.model_dump())
    db.add(change)
    await db.commit()
    await db.refresh(change)
    return change


async def get_price_change(db: AsyncSession, change_id: int) -> PriceChange | None:
    result = await db.execute(select(PriceChange).where(PriceChange.id == change_id))
    return result.scalar_one_or_none()


async def get_price_changes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    competitor_id: int | None = None,
    change_type: str | None = None,
) -> list[PriceChange]:
    stmt = select(PriceChange)

    if competitor_id is not None:
        stmt = stmt.where(PriceChange.competitor_id == competitor_id)

    if change_type is not None:
        stmt = stmt.where(PriceChange.change_type == change_type)

    stmt = stmt.order_by(desc(PriceChange.detected_at), desc(PriceChange.id)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_latest_price_change(db: AsyncSession, competitor_id: int) -> PriceChange | None:
    stmt = (
        select(PriceChange)
        .where(PriceChange.competitor_id == competitor_id)
        .order_by(desc(PriceChange.detected_at), desc(PriceChange.id))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_price_change(
    db: AsyncSession,
    change: PriceChange,
    change_in: PriceChangeUpdate,
) -> PriceChange:
    update_data = change_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(change, field, value)

    await db.commit()
    await db.refresh(change)
    return change


async def delete_price_change(db: AsyncSession, change: PriceChange) -> None:
    await db.delete(change)
    await db.commit()
