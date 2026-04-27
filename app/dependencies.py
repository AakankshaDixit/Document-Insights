from redis.asyncio import Redis
from app.config import get_settings
settings = get_settings()
_redis = None

async def get_redis() -> Redis:
    global _redis
    if not _redis:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis
