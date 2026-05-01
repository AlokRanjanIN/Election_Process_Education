"""
Middleware configuration for rate limiting, request logging,
and global exception handling.

Rate limits per plan.md:
  - POST /api/v1/faq/ask: 10/minute per IP
  - GET /api/v1/timeline:  30/minute per IP
  - Default:               60/minute per IP
"""

import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.config import settings

logger = logging.getLogger(__name__)

# --- Rate Limiter (per-instance in-memory, Cloud Run compatible) ---
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    storage_uri="memory://",
)


def handle_rate_limit_exceeded(request: Request, exc: Exception) -> JSONResponse:
    """Return 429 with clear message when rate limit is hit."""
    if not isinstance(exc, RateLimitExceeded):
        logger.warning("Unexpected exception type in rate-limit handler: %s", type(exc))
    logger.warning(
        "Rate limit exceeded: ip=%s, path=%s",
        get_remote_address(request),
        request.url.path,
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after_seconds": 60,
        },
    )


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """Log request method, path, and response time."""
    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    response.headers.setdefault("Cache-Control", "no-store, max-age=0")
    response.headers.setdefault("Pragma", "no-cache")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(self), geolocation=()",
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; frame-ancestors 'none'; base-uri 'self'",
    )
    if settings.ENVIRONMENT.lower() == "production":
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )

    # Do NOT log raw query payloads for privacy (plan.md: No-Logging Policy for RAG)
    logger.info(
        "request: method=%s path=%s status=%d duration=%.1fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def configure_middleware(app: FastAPI) -> None:
    """Attach all middleware to the FastAPI application."""
    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, handle_rate_limit_exceeded)

    # Request logging
    app.middleware("http")(request_logging_middleware)
