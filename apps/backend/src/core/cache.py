# ============================================================
# CodeWhisper PR - Cache Helper
# ============================================================

from redis.asyncio import Redis
from src.core.config import settings

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL)
    return _redis
