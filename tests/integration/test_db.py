from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def test_create_user(session: AsyncSession) -> None:
    """Test creating and retrieving a user from the database.

    Verifies that a user can be created, committed to the database,
    and retrieved with the correct attributes.
    """
    new_user = User(username='alice', password='secret', email='teste@test')
    session.add(new_user)
    await session.commit()  # Async commit

    # Select the user asynchronously
    result = await session.execute(
        select(User).where(User.username == 'alice')
    )
    user = result.scalar_one()  # Get the first result

    assert user.username == 'alice'
