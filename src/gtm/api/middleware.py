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
    """Redis-backed rate limiter for auth and analysis endpoints.

    Uses Redis INCR with TTL for a sliding window per IP+path.
    Horizontally safe across multiple workers/instances.
    Falls back to pass-through if Redis is unavailable.
    """

    def __init__(self, app, *, requests_per_minute: int = 30, burst: int = 10):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.burst = burst
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

        # Redis-backed counter with 60s TTL
        try:
            from gtm.storage.redis_client import get_redis
            r = get_redis()
            redis_key = f"ratelimit:{client_ip}:{path}"
            current = r.incr(redis_key)
            if current == 1:
                r.expire(redis_key, 60)  # 60 second window

            if current > limit:
                ttl = r.ttl(redis_key)
                logger.warning("Rate limit exceeded: %s on %s (%d/%d)", client_ip, path, current, limit)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                    headers={"Retry-After": str(max(ttl, 1))},
                )
        except Exception:
            # Redis unavailable — fail open (allow request)
            logger.debug("Rate limit check skipped — Redis unavailable")

        return await call_next(request)
