from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=settings.POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
        pool_recycle=settings.POOL_RECYCLE,
        pool_timeout=settings.POOL_TIMEOUT,
    )


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and yield an async database session for dependency injection.

    :return: An AsyncSession instance for database operations.
    """
    session_local = get_sessionmaker()
    async with session_local() as session:
        try:
            yield session  # ruff:ignore[yield-in-context-manager-in-async-generator]
            await session.commit()
        except Exception:
            await session.rollback()
            raise
