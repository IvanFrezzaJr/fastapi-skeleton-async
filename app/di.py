from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.services import auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')

SessionDep = Annotated[
    AsyncSession,
    Depends(get_session),
]

TokenDep = Annotated[
    str,
    Depends(oauth2_scheme),
]

OAuth2FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def current_user(
    session: SessionDep,
    token: TokenDep,
) -> User:
    return await auth.get_current_user(session, token)


CurrentUserDep = Annotated[
    User,
    Depends(current_user),
]
