# ruff: noqa
# mypy: ignore-errors

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.di import CurrentUserDep, SessionDep
from app.models import User
from app.schemas import (
    Message,
    Page,
    UserPublic,
    UserSchema,
)
from app.services.auth import get_current_user
from app.services.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
    get_user,
    list_users,
)
from app.services.user import (
    create_user as create_user_service,
)
from app.services.user import (
    delete_user as delete_user_service,
)
from app.services.user import (
    update_user as update_user_service,
)

router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
)
async def create_user(
    user: UserSchema,
    session: SessionDep,
):
    """
    Create a new user and return it with a 201 Created status.

    :param user: The UserSchema containing user data.
    :param session: The async database session.
    """
    try:
        return await create_user_service(session, user)

    except UserAlreadyExistsError as error:
        detail = (
            'Username already exists'
            if str(error) == 'username'
            else 'Email already exists'
        )

        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=detail,
        ) from error


@router.get('/', response_model=Page[UserPublic])
async def read_users(
    session: SessionDep,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Retrieve a paginated list of all users.

    :param session: The async database session.
    :param limit: Maximum number of users to return.
    :param offset: Number of users to skip.
    """
    users, total = await list_users(session, limit, offset)
    return Page(items=users, total=total, limit=limit, offset=offset)


@router.get('/{user_id}', response_model=UserPublic)
async def read_user(
    user_id: int,
    session: SessionDep,
):
    """
    Retrieve a user by ID.

    :param user_id: The ID of the user to retrieve.
    :param session: The async database session.
    """
    try:
        return await get_user(session, user_id)

    except UserNotFoundError as error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        ) from error


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """
    Update a user's information.

    Only the user themselves can update their own profile.

    :param user_id: The ID of the user to update.
    :param user: The UserSchema containing updated data.
    :param session: The async database session.
    :param current_user: The authenticated user from the token.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not found permission',
        )

    try:
        return await update_user_service(
            session,
            current_user,
            user,
        )

    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        ) from error


@router.delete('/{user_id}', response_model=Message)
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """
    Delete a user by ID.

    Only the user themselves can delete their own account.

    :param user_id: The ID of the user to delete.
    :param session: The async database session.
    :param current_user: The authenticated user from the token.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not found permission',
        )

    await delete_user_service(session, current_user)

    return {'message': 'User deleted'}
