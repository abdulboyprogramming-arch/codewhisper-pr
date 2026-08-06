# ============================================================
# CodeWhisper PR - Cache Service
# ============================================================

import json
import redis
from typing import Any, Optional, Callable, Awaitable
from loguru import logger

from src.core.config import settings


class CacheService:
    """Service for caching operations using Redis."""

    def __init__(self):
        try:
            self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}. Cache will be disabled.")
            self.client = None

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        if not self.client:
            return False

        try:
            serialized = json.dumps(value)
            ttl = ttl or settings.REDIS_CACHE_TTL
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.client:
            return False

        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists check failed for key {key}: {str(e)}")
            return False

    async def clear(self) -> bool:
        """Clear all cache."""
        if not self.client:
            return False

        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache clear failed: {str(e)}")
            return False

    async def get_or_set(
        self, key: str, func: Callable, ttl: Optional[int] = None
    ) -> Any:
        """Get from cache or set using function."""
        value = await self.get(key)
        if value is not None:
            return value

        value = await func() if isinstance(func, Callable) and func.__code__.co_flags & 0x100 else func
        if callable(func):
            import inspect
            if inspect.iscoroutinefunction(func):
                value = await func()
            else:
                value = func()

        if value is not None:
            await self.set(key, value, ttl)

        return value

    def build_key(self, *args, **kwargs) -> str:
        """Build a cache key from components."""
        parts = [str(arg) for arg in args]
        if kwargs:
            parts.append(":".join(f"{k}={v}" for k, v in sorted(kwargs.items())))
        return ":".join(parts)
