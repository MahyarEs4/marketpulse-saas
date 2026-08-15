from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.crud.price_snapshot import (
    create_price_snapshot,
    delete_price_snapshot,
    get_latest_price_snapshot,
    get_price_snapshot,
    get_price_snapshots,
    update_price_snapshot,
)
from app.models.competitor import Competitor
from app.models.price_snapshot import PriceSnapshot
from app.schemas.price_snapshot import PriceSnapshotCreate, PriceSnapshotUpdate


@pytest.mark.asyncio
async def test_create_price_snapshot(db_session):
    competitor = Competitor(name="CRUD Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    snapshot_in = PriceSnapshotCreate(
        competitor_id=competitor.id,
        source_url="https://example.com/item",
        title="Item Title",
        currency="IRR",
        price=Decimal("500000"),
        old_price=Decimal("450000"),
        notes="Created via CRUD",
        captured_at=datetime.now(timezone.utc),
    )

    snapshot = await create_price_snapshot(db_session, snapshot_in)

    assert snapshot.id is not None
    assert snapshot.competitor_id == competitor.id
    assert snapshot.price == Decimal("500000")


@pytest.mark.asyncio
async def test_get_price_snapshot(db_session):
    competitor = Competitor(name="Get Snapshot Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item",
        title="Item Title",
        currency="IRR",
        price=Decimal("700000"),
        old_price=Decimal("650000"),
        notes="Get test",
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    found = await get_price_snapshot(db_session, snapshot.id)

    assert found is not None
    assert found.id == snapshot.id
    assert found.price == Decimal("700000")


@pytest.mark.asyncio
async def test_get_price_snapshots_filters_by_competitor(db_session):
    competitor1 = Competitor(name="Competitor 1")
    competitor2 = Competitor(name="Competitor 2")
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

    results = await get_price_snapshots(db_session, competitor_id=competitor1.id)

    assert len(results) == 1
    assert results[0].competitor_id == competitor1.id


@pytest.mark.asyncio
async def test_get_latest_price_snapshot(db_session):
    competitor = Competitor(name="Latest Snapshot Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    first_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/1",
        title="First",
        currency="IRR",
        price=Decimal("100000"),
        captured_at=datetime(2026, 7, 26, 10, 0, tzinfo=timezone.utc),
    )
    second_snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/2",
        title="Second",
        currency="IRR",
        price=Decimal("150000"),
        captured_at=datetime(2026, 7, 26, 11, 0, tzinfo=timezone.utc),
    )
    db_session.add_all([first_snapshot, second_snapshot])
    await db_session.commit()

    latest = await get_latest_price_snapshot(db_session, competitor.id)

    assert latest is not None
    assert latest.title == "Second"


@pytest.mark.asyncio
async def test_update_price_snapshot(db_session):
    competitor = Competitor(name="Update Snapshot Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item",
        title="Old Title",
        currency="IRR",
        price=Decimal("300000"),
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    update_in = PriceSnapshotUpdate(
        title="New Title",
        price=Decimal("350000"),
        notes="Updated",
    )

    updated = await update_price_snapshot(db_session, snapshot, update_in)

    assert updated.title == "New Title"
    assert updated.price == Decimal("350000")
    assert updated.notes == "Updated"


@pytest.mark.asyncio
async def test_delete_price_snapshot(db_session):
    competitor = Competitor(name="Delete Snapshot Competitor")
    db_session.add(competitor)
    await db_session.commit()
    await db_session.refresh(competitor)

    snapshot = PriceSnapshot(
        competitor_id=competitor.id,
        source_url="https://example.com/item",
        title="Delete Me",
        currency="IRR",
        price=Decimal("400000"),
        captured_at=datetime.now(timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()
    await db_session.refresh(snapshot)

    await delete_price_snapshot(db_session, snapshot)

    found = await get_price_snapshot(db_session, snapshot.id)
    assert found is None
