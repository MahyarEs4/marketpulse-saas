# tests/test_auth_login.py
import pytest
from app.tests.factories import create_test_tenant


@pytest.mark.asyncio
async def test_login_success(client, db_session, unique_slug):
    await create_test_tenant(db_session, slug=unique_slug)

    await client.post("/api/auth/register", json={
        "tenant_slug": unique_slug,
        "email": "login1@example.com",
        "password": "MyPassword1",
        "full_name": "Login One",
    })

    response = await client.post("/api/auth/login", json={
        "tenant_slug": unique_slug,
        "email": "login1@example.com",
        "password": "MyPassword1",
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, db_session, unique_slug):
    await create_test_tenant(db_session, slug=unique_slug)

    await client.post("/api/auth/register", json={
        "tenant_slug": unique_slug,
        "email": "login2@example.com",
        "password": "CorrectPass1",
        "full_name": "Login Two",
    })

    response = await client.post("/api/auth/login", json={
        "tenant_slug": unique_slug,
        "email": "login2@example.com",
        "password": "WrongPass1",
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_tenant_slug(client, db_session, unique_slug):
    await create_test_tenant(db_session, slug=unique_slug)

    await client.post("/api/auth/register", json={
        "tenant_slug": unique_slug,
        "email": "login3@example.com",
        "password": "SomePass1",
        "full_name": "Login Three",
    })

    response = await client.post("/api/auth/login", json={
        "tenant_slug": "wrong-slug-xyz",
        "email": "login3@example.com",
        "password": "SomePass1",
    })

    assert response.status_code == 401
