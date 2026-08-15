from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert_log import AlertLog
from app.schemas.alert_log import AlertLogCreate, AlertLogUpdate


async def create_alert_log(db: AsyncSession, alert_in: AlertLogCreate) -> AlertLog:
    alert = AlertLog(**alert_in.model_dump())
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def get_alert_log(db: AsyncSession, alert_id: int) -> AlertLog | None:
    result = await db.execute(select(AlertLog).where(AlertLog.id == alert_id))
    return result.scalar_one_or_none()


async def update_alert_log(db: AsyncSession, alert: AlertLog, alert_in: AlertLogUpdate) -> AlertLog:
    update_data = alert_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alert, key, value)
    await db.commit()
    await db.refresh(alert)
    return alert


async def mark_alert_sent(db: AsyncSession, alert: AlertLog) -> AlertLog:
    alert.status = "sent"
    alert.sent_at = datetime.now(timezone.utc)
    alert.error_message = None
    await db.commit()
    await db.refresh(alert)
    return alert


async def mark_alert_failed(db: AsyncSession, alert: AlertLog, error_message: str) -> AlertLog:
    alert.status = "failed"
    alert.error_message = error_message
    await db.commit()
    await db.refresh(alert)
    return alert
