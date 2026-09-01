import logging
from collections.abc import AsyncIterator

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pravburo_ref_common.config import get_common_settings

settings = get_common_settings()
logger = logging.getLogger(__name__)
app_metadata = MetaData(schema=settings.referral_db_schema)
engine: AsyncEngine = create_async_engine(settings.database_url, pool_pre_ping=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


async def database_is_ready() -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database readiness check failed: %s", type(exc).__name__)
        return False


async def close_database() -> None:
    await engine.dispose()
