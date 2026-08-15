from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.crud.price_change import create_price_change
from app.models.price_change import PriceChange
from app.models.price_snapshot import PriceSnapshot
from app.schemas.price_change import PriceChangeCreate


class PriceChangeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alert_threshold_percent = settings.PRICE_CHANGE_ALERT_THRESHOLD_PERCENT

    def _calc_change_amount(self, old_price: Decimal, new_price: Decimal) -> Decimal:
        return (new_price - old_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calc_change_percent(self, old_price: Decimal, new_price: Decimal) -> Decimal | None:
        if old_price == 0:
            return None
        percent = ((new_price - old_price) / old_price) * Decimal("100")
        return percent.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _get_change_type(self, change_amount: Decimal) -> str:
        if change_amount > 0:
            return "increase"
        if change_amount < 0:
            return "decrease"
        return "no_change"

    async def _get_previous_snapshot(
        self, competitor_id: int, current_snapshot_id: int
    ) -> PriceSnapshot | None:
        stmt = (
            select(PriceSnapshot)
            .where(
                PriceSnapshot.competitor_id == competitor_id,
                PriceSnapshot.id < current_snapshot_id,
            )
            .order_by(PriceSnapshot.id.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _should_alert(self, change_percent: Decimal | None) -> bool:
        if change_percent is None:
            return False
        return abs(change_percent) >= self.alert_threshold_percent

    async def process_snapshot(
        self, current_snapshot: PriceSnapshot
    ) -> tuple[PriceChange, bool] | None:
        previous_snapshot = await self._get_previous_snapshot(
            current_snapshot.competitor_id,
            current_snapshot.id,
        )

        if previous_snapshot is None:
            return None

        old_price = Decimal(str(previous_snapshot.price))
        new_price = Decimal(str(current_snapshot.price))

        if old_price == new_price:
            return None

        change_amount = self._calc_change_amount(old_price, new_price)
        change_percent = self._calc_change_percent(old_price, new_price)
        change_type = self._get_change_type(change_amount)

        change_in = PriceChangeCreate(
            competitor_id=current_snapshot.competitor_id,
            current_snapshot_id=current_snapshot.id,
            previous_snapshot_id=previous_snapshot.id,
            old_price=old_price,
            new_price=new_price,
            change_amount=change_amount,
            change_percent=change_percent,
            currency=current_snapshot.currency,
            change_type=change_type,
            notes=f"Auto-detected from snapshot {current_snapshot.id}",
            detected_at=current_snapshot.captured_at,
        )

        price_change = await create_price_change(self.db, change_in)
        return price_change, self._should_alert(change_percent)
