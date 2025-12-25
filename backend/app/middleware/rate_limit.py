"""
Rate Limiting Middleware (Phase 3)
Implements sliding window rate limiting with Redis backend.
"""

from typing import Callable, Optional
import time
import hashlib

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class RateLimiter:
    """
    Redis-backed rate limiter using sliding window algorithm.
    Provides per-endpoint and per-user rate limiting.
    """

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis: Optional[redis.Redis] = None

    async def get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _get_key(self, identifier: str, endpoint: str, window: str) -> str:
        """Generate rate limit key."""
        key_data = f"{identifier}:{endpoint}:{window}"
        return f"rate_limit:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def is_rate_limited(
        self,
        identifier: str,
        endpoint: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, dict]:
        """
        Check if request should be rate limited.

        Returns:
            Tuple of (is_limited, info_dict)
        """
        try:
            redis_client = await self.get_redis()
            current_window = int(time.time() // window_seconds)
            key = self._get_key(identifier, endpoint, str(current_window))

            # Increment counter
            current_count = await redis_client.incr(key)

            # Set expiry on first request in window
            if current_count == 1:
                await redis_client.expire(key, window_seconds + 1)

            # Calculate remaining
            remaining = max(0, limit - current_count)
            reset_time = (current_window + 1) * window_seconds

            info = {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time,
                "window_seconds": window_seconds,
            }

            is_limited = current_count > limit

            if is_limited:
                logger.warning(
                    "Rate limit exceeded",
                    identifier=identifier,
                    endpoint=endpoint,
                    count=current_count,
                    limit=limit,
                )

            return is_limited, info

        except redis.RedisError as e:
            logger.error("Redis error in rate limiter", error=str(e))
            # Fail open - allow request if Redis is down
            return False, {"limit": limit, "remaining": limit, "reset": 0}

    async def get_rate_limit_config(self, path: str, method: str) -> tuple[int, int]:
        """
        Get rate limit configuration for endpoint.

        Returns:
            Tuple of (limit, window_seconds)
        """
        # Auth endpoints - strict limits
        if "/auth/login" in path or "/auth/register" in path:
            return settings.RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE, 60

        # Export endpoints - very limited
        if "/export" in path or path.endswith("/export"):
            return settings.RATE_LIMIT_EXPORT_REQUESTS_PER_HOUR, 3600

        # Bulk operations - limited
        if "/bulk" in path or "bulk-import" in path:
            return settings.RATE_LIMIT_BULK_REQUESTS_PER_HOUR, 3600

        # Risk calculation - moderate limits
        if "/risks/calculate" in path:
            return 10, 60

        # Default rate limit
        return settings.RATE_LIMIT_REQUESTS_PER_MINUTE, 60


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.
    """

    def __init__(self, app, limiter: RateLimiter = None):
        super().__init__(app)
        self.limiter = limiter or rate_limiter

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/", "/v1/docs", "/v1/redoc", "/v1/openapi.json"):
            return await call_next(request)

        # Get client identifier
        identifier = self._get_identifier(request)

        # Get rate limit config for this endpoint
        limit, window = await self.limiter.get_rate_limit_config(
            request.url.path,
            request.method,
        )

        # Check rate limit
        is_limited, info = await self.limiter.is_rate_limited(
            identifier=identifier,
            endpoint=f"{request.method}:{request.url.path}",
            limit=limit,
            window_seconds=window,
        )

        if is_limited:
            return Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["reset"] - int(time.time())),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])

        return response

    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting."""
        # Try to get user ID from auth header if available
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Use hashed token as identifier for authenticated users
            token = auth_header[7:]
            return f"user:{hashlib.md5(token.encode()).hexdigest()[:16]}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"
