# Cache the Redis client object instead of creating one for each dependency call.
# Tests override this client to keep async connections within one event loop.

from functools import lru_cache
from redis.asyncio import Redis
from app.core.config import get_settings

@lru_cache
def get_redis_client() -> Redis:
    return Redis.from_url(get_settings().redis_url)
