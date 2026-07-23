from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.security import OAuth2PasswordBearer
from jwt import (
    PyJWTError,
    decode,
    encode,
)
from pwdlib import PasswordHash

from app.core.exceptions import InvalidTokenError
from app.settings import get_settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')

settings = get_settings()


def create_access_token(login: str) -> str:
    """
    Encode a JWT access token with the provided data and expiration time.

    :param login: It should be the username or email
    """
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode = {'sub': login, 'exp': expire, 'scope': 'access'}

    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(login: str) -> str:
    """
    Encode a JWT refresh token with extended expiration.

    :param login: It should be the username or email
    """

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode = {'sub': login, 'exp': expire, 'scope': 'refresh'}

    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except PyJWTError as error:
        raise InvalidTokenError('Could not validate credentials') from error
