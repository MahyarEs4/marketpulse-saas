from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.alert_log import AlertLog
from app.models.competitor import Competitor
from app.models.price_change import PriceChange
from app.models.price_snapshot import PriceSnapshot


@pytest.mark.asyncio
async def test_create_snapshot_triggers_price_change_and_alert(
    client,
    db_session,
    monkeypatch,
):
    competitor = Competitor(name="Test Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    previous_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/old",
        title="Old Title",
        currency="IRR",
        price=Decimal("100000"),
        old_price=None,
        notes="Previous snapshot",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(previous_snapshot)
    await db_session.commit()
    await db_session.refresh(previous_snapshot)

    async def fake_process_snapshot(self, current_snapshot):
        price_change = PriceChange(
            competitor_id=current_snapshot.competitor_id,
            current_snapshot_id=current_snapshot.id,
            previous_snapshot_id=previous_snapshot.id,
            old_price=Decimal("100000"),
            new_price=Decimal("120000"),
            change_amount=Decimal("20000"),
            change_percent=Decimal("20.00"),
            currency="IRR",
            change_type="increase",
            notes="Auto-detected change",
            detected_at=current_snapshot.captured_at,
        )
        db_session.add(price_change)
        await db_session.commit()
        await db_session.refresh(price_change)
        return price_change, True

    async def fake_send_message(self, text):
        return {"ok": True}

    monkeypatch.setattr(
        "app.services.price_change_service.PriceChangeService.process_snapshot",
        fake_process_snapshot,
    )
    monkeypatch.setattr(
        "app.services.telegram_service.TelegramService.send_message",
        fake_send_message,
    )

    payload = {
        "competitor_id": competitor.id,
        "source_url": "https://example.com/new",
        "title": "New Title",
        "currency": "IRR",
        "price": "120000",
        "old_price": "100000",
        "notes": "New snapshot",
    }

    response = await client.post("/pricing/snapshot", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["competitor_id"] == competitor.id
    assert body["price"] == "120000.00"

    result = await db_session.execute(
        select(PriceChange).order_by(PriceChange.id.desc())
    )
    price_change = result.scalars().first()
    assert price_change is not None
    assert price_change.change_type == "increase"
    assert price_change.change_percent == Decimal("20.00")

    result = await db_session.execute(
        select(AlertLog).order_by(AlertLog.id.desc())
    )
    alert_log = result.scalars().first()
    assert alert_log is not None
    assert alert_log.status == "sent"
    assert alert_log.channel == "telegram"
    assert alert_log.price_change_id == price_change.id
    assert "Test Competitor" in alert_log.message


@pytest.mark.asyncio
async def test_alert_log_marked_failed_when_telegram_send_fails(
    client,
    db_session,
    monkeypatch,
):
    competitor = Competitor(name="Failing Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    previous_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/old",
        title="Old Title",
        currency="IRR",
        price=Decimal("150000"),
        old_price=None,
        notes="Previous snapshot",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(previous_snapshot)
    await db_session.commit()
    await db_session.refresh(previous_snapshot)

    async def fake_process_snapshot(self, current_snapshot):
        price_change = PriceChange(
            competitor_id=current_snapshot.competitor_id,
            current_snapshot_id=current_snapshot.id,
            previous_snapshot_id=previous_snapshot.id,
            old_price=Decimal("150000"),
            new_price=Decimal("160000"),
            change_amount=Decimal("10000"),
            change_percent=Decimal("6.67"),
            currency="IRR",
            change_type="increase",
            notes="Trigger failure",
            detected_at=current_snapshot.captured_at,
        )
        db_session.add(price_change)
        await db_session.commit()
        await db_session.refresh(price_change)
        return price_change, True

    async def fake_send_message(self, text):
        raise Exception("Telegram down")

    monkeypatch.setattr(
        "app.services.price_change_service.PriceChangeService.process_snapshot",
        fake_process_snapshot,
    )
    monkeypatch.setattr(
        "app.services.telegram_service.TelegramService.send_message",
        fake_send_message,
    )

    response = await client.post(
        "/pricing/snapshot",
        json={
            "competitor_id": competitor.id,
            "source_url": "https://example.com/new",
            "title": "New Title",
            "currency": "IRR",
            "price": "160000",
            "old_price": "150000",
            "notes": "Trigger failure",
        },
    )

    assert response.status_code == 201

    result = await db_session.execute(
        select(AlertLog).order_by(AlertLog.id.desc())
    )
    alert_log = result.scalars().first()
    assert alert_log is not None
    assert alert_log.status == "failed"
    assert alert_log.channel == "telegram"
    assert alert_log.error_message is not None
    assert "Telegram down" in alert_log.error_message
