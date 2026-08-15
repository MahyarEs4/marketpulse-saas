from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models.competitor import Competitor
from app.models.price_snapshot import PriceSnapshot
from app.services.price_change_service import PriceChangeService


@pytest.mark.asyncio
async def test_process_snapshot_creates_increase_change(db_session):
    competitor = Competitor(name="Service Competitor")
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

    current_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/new",
        title="New Title",
        currency="IRR",
        price=Decimal("120000"),
        old_price=Decimal("100000"),
        notes="Current snapshot",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(current_snapshot)
    await db_session.commit()
    await db_session.refresh(current_snapshot)

    service = PriceChangeService(db_session)
    result = await service.process_snapshot(current_snapshot)

    assert result is not None
    price_change, should_alert = result

    assert should_alert is True
    assert price_change.competitor_id == competitor.id
    assert price_change.current_snapshot_id == current_snapshot.id
    assert price_change.previous_snapshot_id == previous_snapshot.id
    assert price_change.old_price == Decimal("100000")
    assert price_change.new_price == Decimal("120000")
    assert price_change.change_amount == Decimal("20000")
    assert price_change.change_percent == Decimal("20.00")
    assert price_change.change_type == "increase"


@pytest.mark.asyncio
async def test_process_snapshot_creates_decrease_change(db_session):
    competitor = Competitor(name="Decrease Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    previous_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/old",
        title="Old Title",
        currency="IRR",
        price=Decimal("200000"),
        old_price=None,
        notes="Previous snapshot",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(previous_snapshot)
    await db_session.commit()
    await db_session.refresh(previous_snapshot)

    current_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/new",
        title="New Title",
        currency="IRR",
        price=Decimal("150000"),
        old_price=Decimal("200000"),
        notes="Current snapshot",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(current_snapshot)
    await db_session.commit()
    await db_session.refresh(current_snapshot)

    service = PriceChangeService(db_session)
    result = await service.process_snapshot(current_snapshot)

    assert result is not None
    price_change, should_alert = result

    assert should_alert is True
    assert price_change.change_amount == Decimal("-50000")
    assert price_change.change_percent == Decimal("-25.00")
    assert price_change.change_type == "decrease"


@pytest.mark.asyncio
async def test_process_snapshot_returns_none_when_price_unchanged(db_session):
    competitor = Competitor(name="No Change Competitor")
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

    current_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/new",
        title="New Title",
        currency="IRR",
        price=Decimal("100000"),
        old_price=Decimal("100000"),
        notes="Current snapshot",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(current_snapshot)
    await db_session.commit()
    await db_session.refresh(current_snapshot)

    service = PriceChangeService(db_session)
    result = await service.process_snapshot(current_snapshot)

    assert result is None


@pytest.mark.asyncio
async def test_process_snapshot_first_snapshot_returns_none(db_session):
    competitor = Competitor(name="First Snapshot Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    current_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/new",
        title="New Title",
        currency="IRR",
        price=Decimal("100000"),
        old_price=None,
        notes="First snapshot",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(current_snapshot)
    await db_session.commit()
    await db_session.refresh(current_snapshot)

    service = PriceChangeService(db_session)
    result = await service.process_snapshot(current_snapshot)

    assert result is None


@pytest.mark.asyncio
async def test_process_snapshot_zero_previous_price_handles_percent_safely(db_session):
    competitor = Competitor(name="Zero Price Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    previous_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/old",
        title="Old Title",
        currency="IRR",
        price=Decimal("0"),
        old_price=None,
        notes="Zero previous price",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(previous_snapshot)
    await db_session.commit()
    await db_session.refresh(previous_snapshot)

    current_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/new",
        title="New Title",
        currency="IRR",
        price=Decimal("100000"),
        old_price=Decimal("0"),
        notes="Current snapshot",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(current_snapshot)
    await db_session.commit()
    await db_session.refresh(current_snapshot)

    service = PriceChangeService(db_session)
    result = await service.process_snapshot(current_snapshot)

    assert result is not None
    price_change, should_alert = result

    assert should_alert is False
    assert price_change.old_price == Decimal("0")
    assert price_change.new_price == Decimal("100000")
    assert price_change.change_amount == Decimal("100000")
    assert price_change.change_percent is None
    assert price_change.change_type == "increase"
