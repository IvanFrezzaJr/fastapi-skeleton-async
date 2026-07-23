from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services import health


async def test_ping_pong(client: AsyncClient) -> None:
    """Test the ping endpoint returns a pong response.

    Verifies that the GET /status/ping endpoint is accessible and
    returns a simple acknowledgment response.
    """
    response = await client.get('/status/ping')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'pong'}


async def test_health_check_success(client: AsyncClient) -> None:
    """Test the health check endpoint when system is fully operational.

    Verifies that the GET /status/health endpoint returns 200 OK with all
    health indicators (database, system) reporting as healthy.
    """
    response = await client.get('/status/health')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'status': 'ok',
        'database': True,
        'system': True,
    }


async def test_health_check_database_failure(
    app: FastAPI,
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the health check endpoint.

    Verifies that when the database service is unavailable,
    endpoint returns 200 OK with the database indicator set to False
    while system remains healthy, allowing partial degradation handling.
    """
    # Simulate a database service failure
    # Monkeypatch modifies the database_is_healthy function in the test

    mock_session = AsyncMock(spec=AsyncSession)

    # Force the call to raise a connection exception
    mock_session.execute.side_effect = Exception('Database connection failed')
    mock_session.scalar.side_effect = Exception('Database connection failed')

    # Temporarily override the FastAPI dependency on the test app instance
    app.dependency_overrides[get_session] = lambda: mock_session

    monkeypatch.setattr(
        health,
        'database_is_healthy',
        AsyncMock(return_value=False),
    )

    response = await client.get('/status/health')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'status': 'error',
        'database': False,
        'system': True,
    }
