"""Request logging middleware."""
from __future__ import annotations

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..utils.logging import get_logger
import structlog

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests with timing, status, and metadata."""

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        # Bind request context to structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        logger.info("request_started",
                     method=request.method,
                     path=request.url.path,
                     query=str(request.query_params),
                     client=request.client.host if request.client else "unknown")

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error("request_failed",
                         duration_ms=duration_ms,
                         error=str(exc))
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)

        logger.info("request_completed",
                     status_code=response.status_code,
                     duration_ms=duration_ms)

        response.headers["X-Process-Time-Ms"] = str(duration_ms)
        return response
