from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    pass


class InvalidCredentialsError(AppError):
    pass


class InvalidTokenError(AppError):
    pass


class TokenExpiredError(AppError):
    pass


async def invalid_credentials_handler(
    request: Request,
    exc: InvalidCredentialsError,
) -> JSONResponse:
    """
    Handle invalid credentials errors by returning a 400 Bad Request response.

    :param request: The incoming HTTP request.
    :param exc: The InvalidCredentialsError exception instance.
    """
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={'detail': str(exc)},
    )


async def invalid_token_handler(
    request: Request,
    exc: InvalidTokenError,
) -> JSONResponse:
    """
    Handle invalid token errors by returning a 401 Unauthorized response.

    :param request: The incoming HTTP request.
    :param exc: The InvalidTokenError exception instance.
    """
    return JSONResponse(
        status_code=HTTPStatus.UNAUTHORIZED,
        content={'detail': str(exc)},
        headers={'WWW-Authenticate': 'Bearer'},
    )


async def expired_token_handler(
    request: Request,
    exc: InvalidTokenError,
) -> JSONResponse:
    """
    Handle expired token errors by returning a 401 Unauthorized response.

    :param request: The incoming HTTP request.
    :param exc: The InvalidTokenError exception instance.
    """
    return JSONResponse(
        status_code=HTTPStatus.UNAUTHORIZED,
        content={'detail': str(exc)},
        headers={'WWW-Authenticate': 'Bearer'},
    )


T_ExceptionHandler = Callable[..., Any]

EXCEPTION_HANDLERS: list[tuple[type[Exception], T_ExceptionHandler]] = [
    (InvalidCredentialsError, invalid_credentials_handler),
    (InvalidTokenError, invalid_token_handler),
    (TokenExpiredError, expired_token_handler),
]


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers to the FastAPI application.

    Iterates through EXCEPTION_HANDLERS and registers each exception
    class with its corresponding handler.

    :param app: The FastAPI application instance.
    """
    for exc_class, handler in EXCEPTION_HANDLERS:
        app.add_exception_handler(exc_class, handler)
