# services/health.py

import platform
import shutil

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def database_is_healthy(session: AsyncSession) -> bool:
    """
    Check if the database is healthy by executing a simple query.

    :param session: The async database session.
    """
    try:
        await session.execute(text('SELECT 1'))
        return True
    except Exception:
        return False


def command_exists(command: str) -> bool:
    """Check if a command exists in the system PATH."""
    return shutil.which(command) is not None


def is_linux() -> bool:
    """Check if the current system is Linux."""
    return platform.system().lower() == 'linux'


def basic_ok() -> bool:
    """Check if basic system requirements are met."""
    return is_linux()
