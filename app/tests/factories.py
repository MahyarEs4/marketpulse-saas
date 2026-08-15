# app/tests/factories.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant


async def create_test_tenant(db: AsyncSession, slug: str, name: str = "Test Tenant") -> Tenant:
    tenant = Tenant(name=name, slug=slug, is_active=True)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant
