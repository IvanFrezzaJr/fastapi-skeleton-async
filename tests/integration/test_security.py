from http import HTTPStatus

from httpx import AsyncClient

from app.services.jwt import (
    create_access_token,
    decode_token,
)


async def test_jwt() -> None:
    """Test JWT access token creation and payload decoding.

    Verifies that a token can be created with valid subject claim
    and expiration time, and correctly decoded with the secret key.
    """

    login = 'test@test.com'

    token = create_access_token(login)

    result = decode_token(token)

    assert result['sub'] == login
    assert result['exp']


async def test_jwt_invalid_token(client: AsyncClient) -> None:
    """Test that API endpoints reject requests with invalid JWT tokens.

    Verifies that a DELETE request with an invalid authorization header
    returns 401 Unauthorized with the appropriate error message.
    """
    response = await client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
