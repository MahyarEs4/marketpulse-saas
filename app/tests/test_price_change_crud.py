from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.crud.price_change import (
    create_price_change,
    delete_price_change,
    get_latest_price_change,
    get_price_change,get_price_changes,
    update_price_change,
)
from app.models.competitor import Competitor
from app.models.price_change import PriceChange
from app.models.price_snapshot import PriceSnapshot
from app.schemas.price_change import PriceChangeCreate, PriceChangeUpdate


@pytest.mark.asyncio
async def test_create_price_change(db_session):
    competitor = Competitor(name="Change CRUD Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item",
        title="Snapshot",
        currency="IRR",
        price=Decimal("500000"),
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    change_in = PriceChangeCreate(
        competitor_id=competitor.id,
        current_snapshot_id=snapshot.id,
        previous_snapshot_id=None,
        old_price=Decimal("450000"),
        new_price=Decimal("500000"),
        change_amount=Decimal("50000"),
        change_percent=Decimal("11.11"),
        currency="IRR",
        change_type="increase",
        notes="Created via CRUD",
        detected_at=datetime.now(timezone.utc),
    )

    change = await create_price_change(db_session, change_in)

    assert change.id is not None
    assert change.competitor_id == competitor.id
    assert change.change_type == "increase"


@pytest.mark.asyncio
async def test_get_price_change(db_session):
    competitor = Competitor(name="Get Change Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item",
        title="Snapshot",
        currency="IRR",
        price=Decimal("500000"),
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    change = PriceChange(
        competitor_id=competitor.id,
        current_snapshot_id=snapshot.id,
        previous_snapshot_id=None,
        old_price=Decimal("450000"),
        new_price=Decimal("500000"),
        change_amount=Decimal("50000"),
        change_percent=Decimal("11.11"),
        currency="IRR",
        change_type="increase",
        detected_at=datetime.now(timezone.utc),
    )
    db_session.add(change)
    await db_session.commit()
    await db_session.refresh(change)

    found = await get_price_change(db_session, change.id)

    assert found is not None
    assert found.id == change.id
    assert found.change_amount == Decimal("50000")


@pytest.mark.asyncio
async def test_get_price_changes_filters_by_competitor_and_type(db_session):
    competitor1 = Competitor(name="Competitor A")
    competitor2 = Competitor(name="Competitor B")
    db_session.add_all([competitor1, competitor2])
    await db_session.commit()
    await db_session.refresh(competitor1)
    await db_session.refresh(competitor2)

    snap1 = PriceSnapshot(
        competitor_id=competitor1.id,
        source_url="https://example.com/1",
        title="One",
        currency="IRR",
        price=Decimal("100000"),
        captured_at=datetime.now(timezone.utc),
    )
    snap2 = PriceSnapshot(
        competitor_id=competitor2.id,
        source_url="https://example.com/2",
        title="Two",
        currency="IRR",
        price=Decimal("200000"),
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add_all([snap1, snap2])
    await db_session.commit()
    await db_session.refresh(snap1)
    await db_session.refresh(snap2)

    change1 = PriceChange(
        competitor_id=competitor1.id,
        current_snapshot_id=snap1.id,
        previous_snapshot_id=None,
        old_price=Decimal("90000"),
        new_price=Decimal("100000"),
        change_amount=Decimal("10000"),
        change_percent=Decimal("11.11"),
        currency="IRR",
        change_type="increase",
        detected_at=datetime.now(timezone.utc),
    )
    change2 = PriceChange(
        competitor_id=competitor2.id,
        current_snapshot_id=snap2.id,
        previous_snapshot_id=None,
        old_price=Decimal("210000"),
        new_price=Decimal("200000"),
        change_amount=Decimal("-10000"),
        change_percent=Decimal("-4.76"),
        currency="IRR",
        change_type="decrease",
        detected_at=datetime.now(timezone.utc),
    )
    db_session.add_all([change1, change2])
    await db_session.commit()

    results = await get_price_changes(
        db_session,
        competitor_id=competitor1.id,
        change_type="increase",
    )

    assert len(results) == 1
    assert results[0].competitor_id == competitor1.id
    assert results[0].change_type == "increase"


@pytest.mark.asyncio
async def test_get_latest_price_change(db_session):
    competitor = Competitor(name="Latest Change Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    #← FIX: دو snapshot مجزا — هر PriceChange باید current_snapshot_id یکتا داشته باشد
    snapshot1 = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item-v1",
        title="Snapshot v1",
        currency="IRR",
        price=Decimal("500000"),
        captured_at=datetime(2026, 7, 26, 10, 0, tzinfo=timezone.utc),
    )
    snapshot2 = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item-v2",
        title="Snapshot v2",
        currency="IRR",
        price=Decimal("550000"),
        captured_at=datetime(2026, 7, 26, 11, 0, tzinfo=timezone.utc),
    )
    db_session.add_all([snapshot1, snapshot2])
    await db_session.commit()
    await db_session.refresh(snapshot1)
    await db_session.refresh(snapshot2)

    first_change = PriceChange(
        competitor_id=competitor.id,
        current_snapshot_id=snapshot1.id,      # ← snapshot1
        previous_snapshot_id=None,
        old_price=Decimal("450000"),
        new_price=Decimal("500000"),
        change_amount=Decimal("50000"),
        change_percent=Decimal("11.11"),
        currency="IRR",
        change_type="increase",
        detected_at=datetime(2026, 7, 26, 10, 0, tzinfo=timezone.utc),
    )
    second_change = PriceChange(
        competitor_id=competitor.id,
        current_snapshot_id=snapshot2.id,      # ← snapshot2 (یکتا)
        previous_snapshot_id=snapshot1.id,
        old_price=Decimal("500000"),
        new_price=Decimal("550000"),
        change_amount=Decimal("50000"),
        change_percent=Decimal("10.00"),
        currency="IRR",
        change_type="increase",
        detected_at=datetime(2026, 7, 26, 11, 0, tzinfo=timezone.utc),
    )
    db_session.add_all([first_change, second_change])
    await db_session.commit()

    latest = await get_latest_price_change(db_session, competitor.id)

    assert latest is not None
    assert latest.detected_at == datetime(2026, 7, 26, 11, 0, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_update_price_change(db_session):
    competitor = Competitor(name="Update Change Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item",
        title="Snapshot",
        currency="IRR",
        price=Decimal("300000"),
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    change = PriceChange(
        competitor_id=competitor.id,
        current_snapshot_id=snapshot.id,
        previous_snapshot_id=None,
        old_price=Decimal("250000"),
        new_price=Decimal("300000"),
        change_amount=Decimal("50000"),
        change_percent=Decimal("20.00"),
        currency="IRR",
        change_type="increase",
        detected_at=datetime.now(timezone.utc),
    )
    db_session.add(change)
    await db_session.commit()
    await db_session.refresh(change)

    update_in = PriceChangeUpdate(
        change_type="decrease",
        notes="Updated change",
    )

    updated = await update_price_change(db_session, change, update_in)

    assert updated.change_type == "decrease"
    assert updated.notes == "Updated change"


@pytest.mark.asyncio
async def test_delete_price_change(db_session):
    competitor = Competitor(name="Delete Change Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item",
        title="Snapshot",
        currency="IRR",
        price=Decimal("300000"),
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    change = PriceChange(
        competitor_id=competitor.id,
        current_snapshot_id=snapshot.id,
        previous_snapshot_id=None,
        old_price=Decimal("250000"),
        new_price=Decimal("300000"),
        change_amount=Decimal("50000"),
        change_percent=Decimal("20.00"),
        currency="IRR",
        change_type="increase",
        detected_at=datetime.now(timezone.utc),
    )
    db_session.add(change)
    await db_session.commit()
    await db_session.refresh(change)

    await delete_price_change(db_session, change)

    found = await get_price_change(db_session, change.id)
    assert found is None
