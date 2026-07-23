from http import HTTPStatus

from httpx import AsyncClient

from app.models import User
from app.schemas import UserPublic


async def test_create_user(client: AsyncClient) -> None:
    """Test creating a new user via POST request.

    Verifies that a valid user creation request returns 201 Created
    with the correct user data matching the request payload.
    """
    response = await client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


async def test_create_user_400(client: AsyncClient) -> None:
    """Test that creating users with duplicate username or email fails.

    Verifies that attempting to create a second user with an existing
    username or email returns 400 Bad Request with the appropriate error.
    """
    response = await client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CREATED

    response = await client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'valmir@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}

    response = await client.post(
        '/users/',
        json={
            'username': 'valmir',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


async def test_read_users_empty(client: AsyncClient) -> None:
    """Test retrieving users from an empty database.

    Verifies that the GET /users/ endpoint returns a properly formatted
    response with empty items list when no users exist in the database.
    """
    response = await client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    # Ensure the database is empty before starting the tests
    assert response.json() == {
        'items': [],
        'limit': 10,
        'offset': 0,
        'total': 0,
    }


async def test_read_users(client: AsyncClient, user: User) -> None:
    """Test retrieving the list of all users with pagination.

    Verifies that the GET /users/ endpoint returns a paginated response
    containing the test fixture user with correct metadata.
    """
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await client.get('/users/')
    assert response.json() == {
        'items': [user_schema],
        'limit': 10,
        'offset': 0,
        'total': 1,
    }


async def test_read_user(client: AsyncClient, user: User) -> None:
    """Test retrieving a specific user by ID.

    Verifies that the GET /users/{id} endpoint returns the user object
    with all expected fields matching the database record.
    """
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await client.get(f'/users/{user.id}')
    assert response.json() == user_schema


async def test_read_user_404(client: AsyncClient) -> None:
    """Test that reading a non-existent user returns 404 Not Found.

    Verifies that the GET /users/{id} endpoint properly handles requests
    for user IDs that don't exist in the database.
    """
    response = await client.get('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_update_user(
    client: AsyncClient, user: User, token: str
) -> None:
    """Test updating the authenticated user's profile information.

    Verifies that a PUT request with valid JWT token successfully updates
    the user's username, email, and password in the database.
    """

    response = await client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'test',
            'email': 'test@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'test',
        'email': 'test@example.com',
        'id': user.id,
    }


async def test_update_user_integrity_error(
    client: AsyncClient, user: User, token: str
) -> None:
    """Test that updating to duplicate username or email returns 409 Conflict.

    Verifies that attempting to update a user's credentials to match an
    existing user's username or email is properly rejected.
    """
    # Insert Fausto
    response_create = await client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    assert response_create.status_code == HTTPStatus.CREATED
    assert response_create.json() == {
        'username': 'fausto',
        'email': 'fausto@example.com',
        'id': 2,
    }

    # Update fixture to Fausto's username
    response_update = await client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


async def test_update_user_403(
    client: AsyncClient, other_user: User, token: str
) -> None:
    """Test that users cannot update other users' profiles (403 Forbidden).

    Verifies that a user authenticated with a token can only update their
    own profile and receives 403 Forbidden when attempting to modify
    another user.
    """
    response = await client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


async def test_delete_user(
    client: AsyncClient, user: User, token: str
) -> None:
    """Test deleting the authenticated user's account.

    Verifies that a DELETE request with a valid JWT token successfully
    removes the user from the database and returns a success message.
    """
    response = await client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


async def test_delete_user_403(
    client: AsyncClient, other_user: User, token: str
) -> None:
    """Test that users cannot delete other users' accounts (403 Forbidden).

    Verifies that a user authenticated with a token cannot delete another
    user's account and receives 403 Forbidden when attempting to do so.
    """
    response = await client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
