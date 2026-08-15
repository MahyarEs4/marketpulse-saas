# tests/test_auth_register.py
import pytest
from app.tests.factories import create_test_tenant


@pytest.mark.asyncio
async def test_register_success(client, db_session, unique_slug):
    await create_test_tenant(db_session, slug=unique_slug)  # ← خط ۸: await اضافه شد

    response = await client.post("/api/auth/register", json={
        "tenant_slug": unique_slug,
        "email": "user1@example.com",
        "password": "StrongPass123",
        "full_name": "User One",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user1@example.com"
    assert data["tenant_id"] is not None


@pytest.mark.asyncio
async def test_register_duplicate_email_same_tenant(client, db_session, unique_slug):
    await create_test_tenant(db_session, slug=unique_slug)  # ← خط ۲۵: await اضافه شد

    payload = {
        "tenant_slug": unique_slug,
        "email": "dup@example.com",
        "password": "Pass123456",
        "full_name": "Dup User",
    }
    r1 = await client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = await client.post("/api/auth/register", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_register_nonexistent_tenant(client):
    response = await client.post("/api/auth/register", json={
        "tenant_slug": "does-not-exist",
        "email": "ghost@example.com",
        "password": "Pass123456",
        "full_name": "Ghost",
    })
    assert response.status_code == 404
