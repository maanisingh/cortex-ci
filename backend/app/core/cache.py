"""
Caching Layer (Phase 5.2)
Redis-based caching with intelligent invalidation.
"""

import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import structlog

from app.core.config import settings

logger = structlog.get_logger()

T = TypeVar("T")


class CacheManager:
    """
    Redis-based cache manager with TTL and invalidation support.
    """

    def __init__(self):
        self._redis = None
        self._local_cache: dict = {}
        self._enabled = True

    async def _get_redis(self):
        """Get or create Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis

                self._redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except Exception as e:
                logger.warning("Redis not available, using local cache", error=str(e))
                self._redis = None
        return self._redis

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Create a cache key from prefix and arguments."""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = ":".join(key_parts)
        return f"cache:{hashlib.md5(key_str.encode()).hexdigest()[:16]}:{prefix}"

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self._enabled:
            return None

        try:
            redis = await self._get_redis()
            if redis:
                value = await redis.get(key)
                if value:
                    return json.loads(value)
            else:
                return self._local_cache.get(key)
        except Exception as e:
            logger.warning("Cache get failed", key=key, error=str(e))
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> bool:
        """Set value in cache with TTL."""
        if not self._enabled:
            return False

        try:
            serialized = json.dumps(value, default=str)
            redis = await self._get_redis()
            if redis:
                await redis.setex(key, ttl, serialized)
            else:
                self._local_cache[key] = value
            return True
        except Exception as e:
            logger.warning("Cache set failed", key=key, error=str(e))
        return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            redis = await self._get_redis()
            if redis:
                await redis.delete(key)
            else:
                self._local_cache.pop(key, None)
            return True
        except Exception as e:
            logger.warning("Cache delete failed", key=key, error=str(e))
        return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        count = 0
        try:
            redis = await self._get_redis()
            if redis:
                async for key in redis.scan_iter(match=pattern):
                    await redis.delete(key)
                    count += 1
            else:
                keys_to_delete = [k for k in self._local_cache if pattern.replace("*", "") in k]
                for k in keys_to_delete:
                    del self._local_cache[k]
                    count += 1
        except Exception as e:
            logger.warning("Cache invalidation failed", pattern=pattern, error=str(e))
        return count

    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: int = 300,
    ) -> Any:
        """Get from cache or compute and cache."""
        value = await self.get(key)
        if value is not None:
            return value

        value = await factory() if callable(factory) else factory
        await self.set(key, value, ttl)
        return value

    async def clear_all(self) -> bool:
        """Clear all cache entries."""
        try:
            redis = await self._get_redis()
            if redis:
                await redis.flushdb()
            else:
                self._local_cache.clear()
            return True
        except Exception as e:
            logger.error("Cache clear failed", error=str(e))
        return False

    async def get_stats(self) -> dict:
        """Get cache statistics."""
        try:
            redis = await self._get_redis()
            if redis:
                info = await redis.info("stats")
                return {
                    "type": "redis",
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                    "keys": await redis.dbsize(),
                }
            else:
                return {
                    "type": "local",
                    "keys": len(self._local_cache),
                }
        except Exception as e:
            return {"type": "error", "error": str(e)}


# Cache key prefixes
class CacheKeys:
    """Cache key prefixes for different data types."""

    ENTITY = "entity"
    ENTITY_LIST = "entity_list"
    CONSTRAINT = "constraint"
    CONSTRAINT_LIST = "constraint_list"
    RISK_SUMMARY = "risk_summary"
    RISK_TRENDS = "risk_trends"
    DEPENDENCY = "dependency"
    DEPENDENCY_GRAPH = "dependency_graph"
    DASHBOARD = "dashboard"
    ANALYTICS = "analytics"
    USER = "user"
    TENANT = "tenant"


# TTL configurations (in seconds)
class CacheTTL:
    """Cache TTL configurations."""

    SHORT = 60  # 1 minute
    MEDIUM = 300  # 5 minutes
    LONG = 900  # 15 minutes
    HOUR = 3600  # 1 hour
    DAY = 86400  # 24 hours


def cached(
    prefix: str,
    ttl: int = CacheTTL.MEDIUM,
    key_args: list | None = None,
):
    """
    Decorator for caching function results.

    Usage:
        @cached("entity", ttl=300, key_args=["entity_id"])
        async def get_entity(entity_id: str, db: AsyncSession) -> Entity:
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from specified arguments
            cache_key_parts = [prefix]
            if key_args:
                for arg_name in key_args:
                    if arg_name in kwargs:
                        cache_key_parts.append(str(kwargs[arg_name]))
            cache_key = ":".join(cache_key_parts)

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug("Cache hit", key=cache_key)
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                # Convert to serializable format if needed
                if hasattr(result, "to_dict"):
                    cache_value = result.to_dict()
                elif hasattr(result, "__dict__"):
                    cache_value = dict(result.__dict__)
                else:
                    cache_value = result
                await cache_manager.set(cache_key, cache_value, ttl)

            return result

        return wrapper

    return decorator


def invalidate_cache(*patterns: str):
    """
    Decorator to invalidate cache patterns after function execution.

    Usage:
        @invalidate_cache("entity:*", "entity_list:*")
        async def update_entity(entity_id: str, data: dict, db: AsyncSession):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            for pattern in patterns:
                await cache_manager.invalidate_pattern(pattern)
            return result

        return wrapper

    return decorator


# Global cache manager instance
cache_manager = CacheManager()
