from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.competitor import get_competitor
from app.crud.price_change import (
    create_price_change,
    delete_price_change,
    get_latest_price_change,
    get_price_change,
    get_price_changes,
    update_price_change,
)
from app.schemas.price_change import (
    PriceChangeCreate,
    PriceChangeOut,
    PriceChangeUpdate,
)

router = APIRouter(prefix="/pricing", tags=["Pricing Changes"])


@router.post("/change", response_model=PriceChangeOut, status_code=status.HTTP_201_CREATED)
async def create_change(
    change_in: PriceChangeCreate,
    db: AsyncSession = Depends(get_db),
):
    competitor = await get_competitor(db, change_in.competitor_id)
    if competitor is None:
        raise HTTPException(status_code=404, detail="Competitor not found")

    change = await create_price_change(db, change_in)
    return change


@router.get("/change/{change_id}", response_model=PriceChangeOut)
async def read_change(change_id: int, db: AsyncSession = Depends(get_db)):
    change = await get_price_change(db, change_id)
    if change is None:
        raise HTTPException(status_code=404, detail="Price change not found")
    return change


@router.get("/changes", response_model=list[PriceChangeOut])
async def read_changes(
    competitor_id: int | None = Query(default=None, gt=0),
    change_type: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await get_price_changes(
        db,
        skip=skip,
        limit=limit,
        competitor_id=competitor_id,
        change_type=change_type,
    )


@router.get("/latest-change", response_model=PriceChangeOut)
async def read_latest_change(
    competitor_id: int = Query(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    change = await get_latest_price_change(db, competitor_id)
    if change is None:
        raise HTTPException(status_code=404, detail="Latest price change not found")
    return change


@router.put("/change/{change_id}", response_model=PriceChangeOut)
async def edit_change(
    change_id: int,
    change_in: PriceChangeUpdate,
    db: AsyncSession = Depends(get_db),
):
    change = await get_price_change(db, change_id)
    if change is None:
        raise HTTPException(status_code=404, detail="Price change not found")

    return await update_price_change(db, change, change_in)


@router.delete("/change/{change_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_change(change_id: int, db: AsyncSession = Depends(get_db)):
    change = await get_price_change(db, change_id)
    if change is None:
        raise HTTPException(status_code=404, detail="Price change not found")

    await delete_price_change(db, change)
    return None
