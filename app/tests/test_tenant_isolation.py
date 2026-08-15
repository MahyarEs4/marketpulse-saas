import pytest
from app.tests.factories import create_test_tenant


@pytest.mark.asyncio
async def test_same_email_allowed_across_different_tenants(client, db_session):
    tenant_a = await create_test_tenant(db_session, slug="tenant-a-iso")
    tenant_b = await create_test_tenant(db_session, slug="tenant-b-iso")

    email = "shared@example.com"

    r1 = await client.post("/api/auth/register", json={
        "tenant_slug": tenant_a.slug,
        "email": email,
        "password": "PassA12345",
        "full_name": "User A",
    })
    r2 = await client.post("/api/auth/register", json={
        "tenant_slug": tenant_b.slug,
        "email": email,
        "password": "PassB12345",
        "full_name": "User B",
    })

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["tenant_id"] != r2.json()["tenant_id"]


@pytest.mark.asyncio
async def test_login_fails_when_user_registered_in_other_tenant(client, db_session):
    tenant_a = await create_test_tenant(db_session, slug="tenant-a-cross")
    tenant_b = await create_test_tenant(db_session, slug="tenant-b-cross")

    await client.post("/api/auth/register", json={
        "tenant_slug": tenant_a.slug,
        "email": "crossuser@example.com",
        "password": "CrossPass1",
        "full_name": "Cross User",
    })

    response = await client.post("/api/auth/login", json={
        "tenant_slug": tenant_b.slug,
        "email": "crossuser@example.com",
        "password": "CrossPass1",
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_tenant_id_matches_registered_tenant(client, db_session):
    from app.core.security import decode_token

    tenant = await create_test_tenant(db_session, slug="tenant-token-check")

    await client.post("/api/auth/register", json={
        "tenant_slug": tenant.slug,
        "email": "tokencheck@example.com",
        "password": "TokenPass1",
        "full_name": "Token Check",
    })

    login_response = await client.post("/api/auth/login", json={
        "tenant_slug": tenant.slug,
        "email": "tokencheck@example.com",
        "password": "TokenPass1",
    })

    access_token = login_response.json()["access_token"]
    payload = decode_token(access_token)

    assert payload is not None
    assert payload["tenant_id"] == str(tenant.id)
