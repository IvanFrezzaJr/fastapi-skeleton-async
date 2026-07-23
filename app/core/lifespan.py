from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import logger
from app.database import get_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages initialization (startup) and shutdown events."""

    engine = get_engine()

    logger.info('FastAPI application starting...')

    yield  # Application stays running serving requests here

    logger.info('Shutdown signal received. Starting Graceful Shutdown...')

    try:
        logger.info('Closing database connection pool...')
        await engine.dispose()
        logger.info('Database connections closed successfully.')

    except Exception as exc:
        logger.error(
            f'Error closing connections on shutdown: {exc}', exc_info=True
        )

    logger.info('Process safely completed.')
