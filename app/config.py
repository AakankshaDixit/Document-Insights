from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    log_level: str = "INFO"
    max_active_jobs_per_user: int = 3
    cache_ttl_seconds: int = 3600

@lru_cache
def get_settings() -> Settings:
    return Settings()