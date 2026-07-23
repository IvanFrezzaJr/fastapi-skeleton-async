# app/middlewares.py
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.core.logging import logger


class RequestIDAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(  # ruff:ignore[no-self-use]
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Handle request processing with request ID tracking and logging.

        Generates or retrieves request ID, logs request/response with timing,
        and injects ID in response headers.
        """

        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()
        logger.info(f'[{request_id}] -> {request.method} {request.url.path}')

        try:
            response = await call_next(request)

            process_time_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f'[{request_id}] <- {request.method} {request.url.path} '
                f'- Status: {response.status_code} ({process_time_ms:.2f}ms)'
            )

            response.headers['X-Request-ID'] = request_id
            return response

        except Exception as exc:
            logger.error(
                f'[{request_id}] Unhandled error: {exc}', exc_info=True
            )
            raise exc
