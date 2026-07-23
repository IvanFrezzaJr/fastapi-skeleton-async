from fastapi import FastAPI

from app.api.v1 import auth, status, user
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.core.middlewares import RequestIDAndLoggingMiddleware
from app.settings import get_settings


def create_app() -> FastAPI:

    setup_logging()

    settings = get_settings()

    app = FastAPI(
        lifespan=lifespan,
        docs_url='/docs' if settings.ENVIRONMENT != 'production' else None,
        redoc_url=None,
        openapi_url=(
            '/openapi.json' if settings.ENVIRONMENT != 'production' else None
        ),
    )

    # registrar middlewares
    app.add_middleware(RequestIDAndLoggingMiddleware)

    # Registrar handlers de exceção
    register_exception_handlers(app)

    # Routers
    app.include_router(status.router)
    app.include_router(user.router)
    app.include_router(auth.router)

    return app


app = create_app()
