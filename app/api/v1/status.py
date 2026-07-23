# ruff: noqa
# mypy: ignore-errors

from http import HTTPStatus

from fastapi import APIRouter

from app.di import SessionDep
from app.services.health import (
    basic_ok,
    database_is_healthy,
)

router = APIRouter(
    prefix='/status',
    tags=['status'],
)


@router.get('/ping', status_code=HTTPStatus.OK)
async def ping_pong():
    """Return a pong message in response to a ping request."""
    return {'message': 'pong'}


@router.get('/health', status_code=HTTPStatus.OK)
async def health_check(
    session: SessionDep,
):
    """
    Check the health status of the application and its dependencies.

    :param session: The async database session.
    """
    database_ok = await database_is_healthy(session)

    return {
        'status': 'ok' if database_ok and basic_ok() else 'error',
        'database': database_ok,
        'system': basic_ok(),
    }
