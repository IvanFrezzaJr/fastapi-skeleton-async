from collections.abc import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import get_session
from app.main import create_app
from app.models import User, table_registry
from app.services.jwt import create_access_token
from app.services.password import get_password_hash

# In-memory asynchronous SQLite engine for tests
TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'


@pytest_asyncio.fixture(scope='session')
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create an in-memory test database engine and set up schema.

    Creates all tables before tests and removes them after completion.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={'check_same_thread': False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an isolated database session for each test.

    Rolls back all changes after the test completes to ensure isolation.
    """
    connection = await engine.connect()
    transaction = await connection.begin()

    async_session = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    # Rollback all changes made during this specific test
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def app(session: AsyncSession) -> AsyncGenerator[FastAPI, None]:
    """
    Create a FastAPI application instance configured for testing.
    """

    test_app = create_app()

    def get_session_override() -> AsyncSession:
        return session

    test_app.dependency_overrides[get_session] = get_session_override

    yield test_app

    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client using the test application.
    """

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def user(session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        username='test',
        email='test@example.com',
        password=get_password_hash('password123'),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_user(session: AsyncSession) -> User:
    """Create a second test user for testing permission scenarios."""
    user = User(
        username='test2',
        email='test2@example.com',
        password=get_password_hash('password123'),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def token(user: User) -> str:
    """Generate a valid JWT access token using create_token_pair."""
    return create_access_token(user.email)
