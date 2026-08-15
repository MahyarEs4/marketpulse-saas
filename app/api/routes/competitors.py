from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.competitor import (
    count_competitors,
    create_competitor,
    delete_competitor,
    get_competitor,
    get_competitors,
    update_competitor,
)
from app.schemas.competitor import CompetitorCreate, CompetitorOut, CompetitorUpdate

router = APIRouter(prefix="/competitors", tags=["Competitors"])


@router.get("", response_model=list[CompetitorOut])
async def read_competitors(
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=1000),
    search: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await get_competitors(db=db, skip=skip, limit=limit, search=search, is_active=is_active)


@router.get("/count")
async def read_competitors_count(
    search: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    return {"count": await count_competitors(db=db, search=search, is_active=is_active)}


@router.get("/{competitor_id}", response_model=CompetitorOut)
async def read_competitor(competitor_id: int, db: AsyncSession = Depends(get_db)):
    competitor = await get_competitor(db, competitor_id)
    if competitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found",
        )
    return competitor


@router.post("", response_model=CompetitorOut, status_code=status.HTTP_201_CREATED)
async def create_competitor_view(
    competitor_in: CompetitorCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await create_competitor(db=db, competitor_in=competitor_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{competitor_id}", response_model=CompetitorOut)
async def update_competitor_view(
    competitor_id: int,
    competitor_in: CompetitorUpdate,
    db: AsyncSession = Depends(get_db),
):
    competitor = await get_competitor(db, competitor_id)
    if competitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found",
        )

    try:
        return await update_competitor(db=db, competitor=competitor, competitor_in=competitor_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_competitor_view(competitor_id: int, db: AsyncSession = Depends(get_db)):
    competitor = await get_competitor(db, competitor_id)
    if competitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found",
        )

    await delete_competitor(db=db, competitor=competitor)
    return None
