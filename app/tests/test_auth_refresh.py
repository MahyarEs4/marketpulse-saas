# tests/test_auth_refresh.py
import pytest
from app.tests.factories import create_test_tenant


@pytest.mark.asyncio
async def test_refresh_success(client, db_session, unique_slug):
    await create_test_tenant(db_session, slug=unique_slug)  # ← خط ۸: await اضافه شد

    await client.post("/api/auth/register", json={
        "tenant_slug": unique_slug,
        "email": "refresh1@example.com",
        "password": "RefreshPass1",
        "full_name": "Refresh User",
    })

    login_response = await client.post("/api/auth/login", json={
        "tenant_slug": unique_slug,
        "email": "refresh1@example.com",
        "password": "RefreshPass1",
    })
    refresh_token = login_response.json()["refresh_token"]

    response = await client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client):
    response = await client.post("/api/auth/refresh", json={
        "refresh_token": "invalid.token.here",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rejects_access_token(client, db_session, unique_slug):
    """توکن access نباید در endpoint رفرش پذیرفته شود."""
    await create_test_tenant(db_session, slug=unique_slug)  # ← خط ۴۵: await اضافه شد

    await client.post("/api/auth/register", json={
        "tenant_slug": unique_slug,
        "email": "refresh2@example.com",
        "password": "RefreshPass2",
        "full_name": "Refresh Two",
    })

    login_response = await client.post("/api/auth/login", json={
        "tenant_slug": unique_slug,
        "email": "refresh2@example.com",
        "password": "RefreshPass2",
    })
    access_token = login_response.json()["access_token"]

    response = await client.post("/api/auth/refresh", json={
        "refresh_token": access_token,
    })
    assert response.status_code == 401
