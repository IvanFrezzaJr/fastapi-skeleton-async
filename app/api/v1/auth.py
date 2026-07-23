from fastapi import APIRouter

from app.di import OAuth2FormDep, SessionDep
from app.models import User
from app.schemas import LoginRequest, RefreshTokenRequest, TokenResponse
from app.services import auth
from app.services.jwt import create_access_token, create_refresh_token

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


def _create_token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
        token_type='Bearer',
    )


@router.post('/login', response_model=TokenResponse)
async def login_json(
    session: SessionDep,
    payload: LoginRequest,
) -> TokenResponse:
    """Authenticate user via JSON request."""

    user = await auth.authenticate_user(
        session,
        payload.email,
        payload.password,
    )

    return _create_token_response(user)


@router.post('/token', response_model=TokenResponse)
async def login_form(
    session: SessionDep,
    form_data: OAuth2FormDep,
) -> TokenResponse:
    """Authenticate user via OAuth2 password form."""

    user = await auth.authenticate_user(
        session,
        form_data.username,
        form_data.password,
    )

    return _create_token_response(user)


@router.post('/refresh', response_model=TokenResponse)
async def refresh_token(
    session: SessionDep,
    payload: RefreshTokenRequest,
) -> TokenResponse:
    """Generate new tokens using a valid refresh token."""

    current_user = await auth.get_current_user_for_refresh(
        session,
        payload.refresh_token,
    )

    return _create_token_response(current_user)
