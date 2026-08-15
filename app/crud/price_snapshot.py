from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_snapshot import PriceSnapshot
from app.schemas.price_snapshot import PriceSnapshotCreate, PriceSnapshotUpdate


async def create_price_snapshot(db: AsyncSession, snapshot_in: PriceSnapshotCreate) -> PriceSnapshot:
    snapshot = PriceSnapshot(**snapshot_in.model_dump())
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot


async def get_price_snapshot(db: AsyncSession, snapshot_id: int) -> PriceSnapshot | None:
    result = await db.execute(select(PriceSnapshot).where(PriceSnapshot.id == snapshot_id))
    return result.scalar_one_or_none()


async def get_price_snapshots(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    competitor_id: int | None = None,
) -> list[PriceSnapshot]:
    stmt = select(PriceSnapshot)

    if competitor_id is not None:
        stmt = stmt.where(PriceSnapshot.competitor_id == competitor_id)

    stmt = stmt.order_by(desc(PriceSnapshot.captured_at), desc(PriceSnapshot.id)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_latest_price_snapshot(db: AsyncSession, competitor_id: int) -> PriceSnapshot | None:
    stmt = (
        select(PriceSnapshot)
        .where(PriceSnapshot.competitor_id == competitor_id)
        .order_by(desc(PriceSnapshot.captured_at), desc(PriceSnapshot.id))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_price_snapshot(
    db: AsyncSession,
    snapshot: PriceSnapshot,
    snapshot_in: PriceSnapshotUpdate,
) -> PriceSnapshot:
    update_data = snapshot_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(snapshot, field, value)

    await db.commit()
    await db.refresh(snapshot)
    return snapshot


async def delete_price_snapshot(db: AsyncSession, snapshot: PriceSnapshot) -> None:
    await db.delete(snapshot)
    await db.commit()
