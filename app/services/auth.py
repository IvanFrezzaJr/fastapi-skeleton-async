from typing import Literal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.models import User
from app.services.jwt import decode_token
from app.services.password import verify_password


async def authenticate_user(
    session: AsyncSession,
    login: str,
    password: str,
) -> User:
    """Authenticate a user using email/username and password."""

    user = await _get_user_by_login(session, login)

    if user is None or not verify_password(password, user.password):
        raise InvalidCredentialsError('Incorrect email or password')

    return user


async def get_current_user(
    session: AsyncSession,
    token: str,
) -> User:
    """Return the authenticated user from an access token."""

    return await _get_user_from_token(
        session,
        token,
        expected_scope='access',
    )


async def get_current_user_for_refresh(
    session: AsyncSession,
    token: str,
) -> User:
    """Return the authenticated user from a refresh token."""

    return await _get_user_from_token(
        session,
        token,
        expected_scope='refresh',
    )


async def _get_user_from_token(
    session: AsyncSession,
    token: str,
    expected_scope: Literal['access', 'refresh'],
) -> User:
    """Resolve a user from a JWT token."""

    payload = decode_token(token)

    login = payload.get('sub')
    scope = payload.get('scope')

    if login is None or scope != expected_scope:
        raise InvalidTokenError('Could not validate credentials A')

    user = await _get_user_by_login(session, login)

    if user is None:
        raise InvalidTokenError('Could not validate credentials B')

    return user


async def _get_user_by_login(
    session: AsyncSession,
    login: str,
) -> User | None:
    """Return a user by email or username."""

    result = await session.scalars(
        select(User).where(
            or_(
                User.email == login,
                User.username == login,
            )
        )
    )

    return result.first()
