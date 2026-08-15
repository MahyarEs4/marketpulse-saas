from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory, get_db
from app.crud.alert_log import create_alert_log, get_alert_log, mark_alert_failed, mark_alert_sent
from app.crud.competitor import get_competitor
from app.crud.price_snapshot import (
    create_price_snapshot,
    delete_price_snapshot,
    get_latest_price_snapshot,
    get_price_snapshot,
    get_price_snapshots,
    update_price_snapshot,
)
from app.schemas.alert_log import AlertLogCreate
from app.schemas.price_snapshot import PriceSnapshotCreate, PriceSnapshotOut, PriceSnapshotUpdate
from app.services.price_alert_formatter import format_price_change_alert
from app.services.price_change_service import PriceChangeService
from app.services.telegram_service import TelegramService

router = APIRouter(prefix="/pricing", tags=["Pricing"])


async def send_alert_and_update_log(alert_log_id: int) -> None:
    """Background task: session مستقل می‌سازد تا به request اصلی وابسته نباشد."""
    async with async_session_factory() as db:
        try:
            alert_log = await get_alert_log(db, alert_log_id)
            if alert_log is None:
                return

            telegram_service = TelegramService()
            await telegram_service.send_message(alert_log.message)
            await mark_alert_sent(db, alert_log)

        except Exception as exc:
            # session هنوز باز است، alert_log را refresh نمی‌خواهیم
            # فقط مجدد از DB می‌خوانیم تا object detached نباشد
            alert_log = await get_alert_log(db, alert_log_id)
            if alert_log is not None:
                await mark_alert_failed(db, alert_log, str(exc))


@router.post("/snapshot", response_model=PriceSnapshotOut, status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    snapshot_in: PriceSnapshotCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    competitor = await get_competitor(db, snapshot_in.competitor_id)
    if competitor is None:
        raise HTTPException(status_code=404, detail="Competitor not found")

    snapshot = await create_price_snapshot(db, snapshot_in)

    change_service = PriceChangeService(db=db)
    result = await change_service.process_snapshot(snapshot)

    if result is not None:
        price_change, should_alert = result

        if should_alert:
            competitor_name = competitor.name or f"Competitor #{competitor.id}"

            old_price = Decimal(str(price_change.old_price))
            new_price = Decimal(str(price_change.new_price))
            change_amount = Decimal(str(price_change.change_amount))
            change_percent = (
                Decimal(str(price_change.change_percent))
                if price_change.change_percent is not None
                else None
            )

            message = format_price_change_alert(
                competitor_name=competitor_name,
                old_price=old_price,
                new_price=new_price,
                change_amount=change_amount,
                change_percent=change_percent,
                currency=price_change.currency,
            )

            alert_log = await create_alert_log(
                db,
                AlertLogCreate(
                    price_change_id=price_change.id,
                    channel="telegram",
                    status="pending",
                    message=message,
                    error_message=None,
                    sent_at=None,
                ),
            )

            background_tasks.add_task(send_alert_and_update_log, alert_log.id)

    return snapshot


@router.get("/snapshot/{snapshot_id}", response_model=PriceSnapshotOut)
async def read_snapshot(snapshot_id: int, db: AsyncSession = Depends(get_db)):
    snapshot = await get_price_snapshot(db, snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Price snapshot not found")
    return snapshot


@router.get("/history", response_model=list[PriceSnapshotOut])
async def read_history(
    competitor_id: int | None = Query(default=None, gt=0),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await get_price_snapshots(db, skip=skip, limit=limit, competitor_id=competitor_id)


@router.get("/latest", response_model=PriceSnapshotOut)
async def read_latest(competitor_id: int = Query(..., gt=0), db: AsyncSession = Depends(get_db)):
    snapshot = await get_latest_price_snapshot(db, competitor_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Latest price snapshot not found")
    return snapshot


@router.put("/snapshot/{snapshot_id}", response_model=PriceSnapshotOut)
async def edit_snapshot(
    snapshot_id: int,
    snapshot_in: PriceSnapshotUpdate,
    db: AsyncSession = Depends(get_db),
):
    snapshot = await get_price_snapshot(db, snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Price snapshot not found")

    return await update_price_snapshot(db, snapshot, snapshot_in)


@router.delete("/snapshot/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_snapshot(snapshot_id: int, db: AsyncSession = Depends(get_db)):
    snapshot = await get_price_snapshot(db, snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Price snapshot not found")

    await delete_price_snapshot(db, snapshot)
    return None
