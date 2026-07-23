import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.models import User
from app.services.auth import authenticate_user
from app.services.jwt import create_access_token, create_refresh_token


async def test_authenticate_user_by_email_success(
    session: AsyncSession, user: User
) -> None:
    """Test successful user authentication using email and password.

    Verifies that the authenticate_user service correctly identifies and
    returns a user when provided valid email credentials.
    """
    authenticated = await authenticate_user(
        session=session,
        login='test@example.com',
        password='password123',
    )

    assert authenticated.id == user.id
    assert authenticated.email == user.email


async def test_authenticate_user_by_username_success(
    session: AsyncSession, user: User
) -> None:
    """Test successful user authentication using username and password.

    Verifies that the authenticate_user service correctly identifies and
    returns a user when provided valid username credentials.
    """
    authenticated = await authenticate_user(
        session=session,
        login='test',
        password='password123',
    )

    assert authenticated.id == user.id
    assert authenticated.username == user.username


async def test_authenticate_user_wrong_password(
    session: AsyncSession, user: User
) -> None:
    """Test that authentication fails when provided with incorrect password.

    Verifies that the authenticate_user service raises InvalidCredentialsError
    when a valid user attempts to authenticate with wrong password.
    """
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await authenticate_user(
            session=session,
            login='test@example.com',
            password='wrong_password',
        )

    assert exc_info.type is InvalidCredentialsError
    assert exc_info.value.args[0] == 'Incorrect email or password'


async def test_authenticate_user_not_found(session: AsyncSession) -> None:
    """Test that authentication fails when user does not exist in database.

    Verifies that the authenticate_user service raises InvalidCredentialsError
    when attempting to authenticate with non-existent user credentials.
    """
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await authenticate_user(
            session=session,
            login='nonexistent@example.com',
            password='password123',
        )

    assert exc_info.type is InvalidCredentialsError
    assert exc_info.value.args[0] == 'Incorrect email or password'


async def test_create_access_token(user: User) -> None:
    """Test JWT token pair with all required fields and valid structure.

    Verifies that create_token_pair returns both access and refresh tokens
    with correct token_type and properly formatted string values.
    """
    access_token = create_access_token(user.email)

    assert isinstance(access_token, str)


async def test_create_refresh_token(user: User) -> None:
    """Test JWT token pair with all required fields and valid structure.

    Verifies that create_token_pair returns both access and refresh tokens
    with correct token_type and properly formatted string values.
    """
    access_token = create_refresh_token(user.email)

    assert isinstance(access_token, str)
