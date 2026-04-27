from app.config import get_settings
from redis.asyncio import Redis

settings = get_settings()

class RateLimitService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.limit = settings.max_active_jobs_per_user

    async def get_active_count(self, user_id: str) -> int:
        v = await self.redis.get(f"ratelimit:{user_id}")
        return int(v) if v else 0

    async def increment(self, user_id: str):
        new_val = await self.redis.incr(f"ratelimit:{user_id}")
        return new_val

    async def decrement(self, user_id: str):
        key = f"ratelimit:{user_id}"
        v = await self.redis.decr(key)
        if v < 0:
            await self.redis.set(key, 0)