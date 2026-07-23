from typing import TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr

T = TypeVar('T')


class Message(BaseModel):
    message: str


class Page[T](BaseModel):
    """Generic paginated response envelope."""

    items: list[T]
    total: int
    limit: int
    offset: int


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    # Ensure UserPublic.model_validate(...).model_dump()
    # validates only by schema attributes: id, username and email
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
