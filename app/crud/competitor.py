from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate


async def get_competitor(db: AsyncSession, competitor_id: int):
    result = await db.execute(select(Competitor).where(Competitor.id == competitor_id))
    return result.scalar_one_or_none()


async def get_competitor_by_website(db: AsyncSession, website: str):
    result = await db.execute(select(Competitor).where(Competitor.website == website))
    return result.scalar_one_or_none()


async def get_competitors(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    is_active: bool | None = None,
):
    stmt = select(Competitor)

    if search is not None:
        stmt = stmt.where(Competitor.name.ilike(f"%{search}%"))

    if is_active is not None:
        stmt = stmt.where(Competitor.is_active == is_active)

    stmt = stmt.order_by(Competitor.id.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def count_competitors(
    db: AsyncSession,
    search: str | None = None,
    is_active: bool | None = None,
):
    stmt = select(func.count(Competitor.id))

    if search is not None:
        stmt = stmt.where(Competitor.name.ilike(f"%{search}%"))

    if is_active is not None:
        stmt = stmt.where(Competitor.is_active == is_active)

    result = await db.execute(stmt)
    return result.scalar_one()


async def create_competitor(db: AsyncSession, competitor_in: CompetitorCreate):
    website_value = str(competitor_in.website) if competitor_in.website is not None else None

    if website_value is not None:
        existing = await get_competitor_by_website(db, website_value)
        if existing is not None:
            raise ValueError("Competitor with this website already exists")

    competitor = Competitor(
        name=competitor_in.name,
        website=website_value,
        phone=competitor_in.phone,
        notes=competitor_in.notes,
        is_active=competitor_in.is_active,
    )
    db.add(competitor)
    await db.commit()
    await db.refresh(competitor)
    return competitor


async def update_competitor(db: AsyncSession, competitor: Competitor, competitor_in: CompetitorUpdate):
    update_data = competitor_in.model_dump(exclude_unset=True)

    if "website" in update_data:
        website_raw = update_data["website"]
        if website_raw is not None:
            website_value = str(website_raw)
            existing = await get_competitor_by_website(db, website_value)

            if existing is not None and existing.id != competitor.id:
                raise ValueError("Competitor with this website already exists")

            update_data["website"] = website_value

    for field, value in update_data.items():
        setattr(competitor, field, value)

    await db.commit()
    await db.refresh(competitor)
    return competitor


async def delete_competitor(db: AsyncSession, competitor: Competitor):
    await db.delete(competitor)
    await db.commit()
