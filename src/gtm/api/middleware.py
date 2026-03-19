"""Security middleware for production hardening."""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # HSTS — only for non-dev (browsers cache this)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter for auth and analysis endpoints.

    Uses a sliding window counter per IP. For production, replace
    with Redis-backed rate limiting.
    """

    def __init__(self, app, *, requests_per_minute: int = 30, burst: int = 10):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.burst = burst
        self._windows: dict[str, list[float]] = {}
        # Paths that get rate-limited
        self._limited_paths = {
            "/api/v1/auth/login": 5,       # 5 per minute
            "/api/v1/analyses": 10,         # 10 per minute (POST only)
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        method = request.method

        # Only rate-limit specific paths
        limit = None
        if path == "/api/v1/auth/login" and method == "POST":
            limit = self._limited_paths["/api/v1/auth/login"]
        elif path == "/api/v1/analyses" and method == "POST":
            limit = self._limited_paths["/api/v1/analyses"]

        if limit is None:
            return await call_next(request)

        # Get client IP (respect X-Forwarded-For behind proxy)
        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"

        key = f"{client_ip}:{path}"
        now = time.time()
        window = 60.0  # 1 minute window

        # Clean old entries
        if key not in self._windows:
            self._windows[key] = []
        self._windows[key] = [t for t in self._windows[key] if t > now - window]

        if len(self._windows[key]) >= limit:
            logger.warning("Rate limit exceeded: %s on %s", client_ip, path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": "60"},
            )

        self._windows[key].append(now)
        return await call_next(request)
