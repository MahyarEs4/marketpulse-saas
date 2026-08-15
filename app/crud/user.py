from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.tenant import Tenant


async def get_tenant_by_slug(db: AsyncSession, slug: str) -> Tenant | None:
    result = await db.execute(
        select(Tenant).where(Tenant.slug == slug, Tenant.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, tenant_id, email: str) -> User | None:
    result = await db.execute(
        select(User).where(User.tenant_id == tenant_id, User.email == email)
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    tenant_id,
    email: str,
    hashed_password: str,
    full_name: str | None,
) -> User:
    user = User(
        tenant_id=tenant_id,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
