from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.competitor import Competitor
from app.models.price_change import PriceChange
from app.models.price_snapshot import PriceSnapshot
from app.services.telegram_service import TelegramService


@pytest.mark.asyncio
async def test_send_message_success(db_session):
    competitor = Competitor(name="Alert Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    # ← FIX: snapshot واقعی برای FK reference
    snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/alert-item",
        title="Alert Snapshot",
        currency="IRR",
        price=Decimal("120000"),
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    price_change = PriceChange(
        competitor_id=competitor.id,
        current_snapshot_id=snapshot.id,      # ← FK واقعی
        previous_snapshot_id=None,
        old_price=Decimal("100000"),
        new_price=Decimal("120000"),
        change_amount=Decimal("20000"),
        change_percent=Decimal("20.00"),
        currency="IRR",
        change_type="increase",
        notes="Alert test",
        detected_at=datetime.now(timezone.utc),# ← صریح برای اطمینان
    )
    db_session.add(price_change)
    await db_session.commit()
    await db_session.refresh(price_change)

    service = TelegramService()

    # ← FIX: MagicMock به جای AsyncMock — json() و raise_for_status() در httpx sync هستند
    mock_response = MagicMock()
    mock_response.json.return_value = {"ok": True}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)):
        result = await service.send_message("Alert test message")

    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_send_message_raises_exception(db_session):
    service = TelegramService()

    with patch(
        "httpx.AsyncClient.post",
        new=AsyncMock(side_effect=Exception("Telegram down")),
    ):
        with pytest.raises(Exception, match="Telegram down"):
            await service.send_message("Alert failure test")
