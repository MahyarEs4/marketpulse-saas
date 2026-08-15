from collections.abc import AsyncGenerator
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# ─── Sync (Alembic / legacy) ────────────────────────────────────────────────
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ─── Async ──────────────────────────────────────────────────────────────────
_parsed = urlsplit(settings.DATABASE_URL)
_async_url = urlunsplit(_parsed._replace(scheme="postgresql+asyncpg"))

async_engine = create_async_engine(_async_url, pool_pre_ping=True)
async_session_factory = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


# ─── Async dependency ────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


# ─── Sync dependency ─────────────────────────────────────────────────────────
def get_db_sync():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
