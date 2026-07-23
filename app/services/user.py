from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserSchema
from app.services.password import get_password_hash


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


async def create_user(
    session: AsyncSession,
    user: UserSchema,
) -> User:
    """
    Create a new user in the database after validation.

    Checks if a user with the same username or email already exists
    before creating a new one. Hashes the password before storage.

    :param session: The async database session.
    :param user: The UserSchema containing user data to create.
    """
    existing_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if existing_user:
        if existing_user.username == user.username:
            raise UserAlreadyExistsError('username')

        raise UserAlreadyExistsError('email')

    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


async def list_users(
    session: AsyncSession,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[User], int]:
    """
    Retrieve a paginated list of users from the database.

    :param session: The async database session.
    :param limit: Maximum number of users to return.
    :param offset: Number of users to skip.
    """

    total_query = select(func.count()).select_from(User)
    total = await session.scalar(total_query)

    users_query = select(User).limit(limit).offset(offset)
    result = await session.execute(users_query)
    users = list(result.scalars().all())

    return users, total or 0


async def get_user(
    session: AsyncSession,
    user_id: int,
) -> User:
    """
    Retrieve a user by ID from the database.

    :param session: The async database session.
    :param user_id: The ID of the user to retrieve.
    """
    user = await session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise UserNotFoundError()

    return user


async def update_user(
    session: AsyncSession,
    user: User,
    data: UserSchema,
) -> User:
    """
    Update an existing user with new data.

    Updates username, password (hashed), and email. Handles
    IntegrityError if the new username or email already exists.

    :param session: The async database session.
    :param user: The User object to update.
    :param data: The UserSchema containing updated user data.
    """
    user.username = data.username
    user.password = get_password_hash(data.password)
    user.email = data.email

    try:
        await session.commit()
        await session.refresh(user)

    except IntegrityError as error:
        await session.rollback()
        raise UserAlreadyExistsError() from error

    return user


async def delete_user(
    session: AsyncSession,
    user: User,
) -> None:
    """
    Delete a user from the database.

    :param session: The async database session.
    :param user: The User object to delete.
    """
    await session.delete(user)
    await session.commit()
