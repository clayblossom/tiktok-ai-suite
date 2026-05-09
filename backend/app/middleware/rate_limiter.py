"""Rate limiting middleware using in-memory sliding window."""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..utils.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter using sliding window counter.

    For production, swap to Redis-backed rate limiting.
    """

    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.rpm_limit = requests_per_minute
        self.rph_limit = requests_per_hour
        # client_id -> list of timestamps
        self._minute_windows: dict[str, list[float]] = defaultdict(list)
        self._hour_windows: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    def _get_client_id(self, request: Request) -> str:
        """Identify client by IP or auth token."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _cleanup_stale(self) -> None:
        """Periodically clean up stale window entries."""
        now = time.time()
        if now - self._last_cleanup < 60:
            return
        self._last_cleanup = now
        cutoff_hour = now - 3600
        stale_clients = [
            cid for cid, times in self._hour_windows.items()
            if not times or times[-1] < cutoff_hour
        ]
        for cid in stale_clients:
            del self._hour_windows[cid]
            self._minute_windows.pop(cid, None)

    def _check_rate(self, client_id: str) -> tuple[bool, str]:
        """Check if request is within rate limits. Returns (allowed, reason)."""
        now = time.time()

        # Clean windows
        minute_window = self._minute_windows[client_id]
        hour_window = self._hour_windows[client_id]

        minute_window[:] = [t for t in minute_window if now - t < 60]
        hour_window[:] = [t for t in hour_window if now - t < 3600]

        if len(hour_window) >= self.rph_limit:
            return False, f"Hourly rate limit exceeded ({self.rph_limit}/hour)"

        if len(minute_window) >= self.rpm_limit:
            return False, f"Minute rate limit exceeded ({self.rpm_limit}/minute)"

        # Record request
        minute_window.append(now)
        hour_window.append(now)
        return True, ""

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks
        if request.url.path == "/api/health":
            return await call_next(request)

        self._cleanup_stale()
        client_id = self._get_client_id(request)

        allowed, reason = self._check_rate(client_id)
        if not allowed:
            logger.warning("rate_limit_hit", client=client_id, path=request.url.path, reason=reason)
            return JSONResponse(
                status_code=429,
                content={"detail": reason},
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.rpm_limit)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.rph_limit)
        return response
