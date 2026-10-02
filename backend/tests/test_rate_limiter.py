# asyncio.run() creates and closes the event loop for this synchronous test.
# Do not call it within an already running event loop.
# Marked pytest-asyncio tests instead use the plugin-managed event loop.
# Inject now_ms to check rolling-window boundaries without waiting.
# At start + 60_000, a request at start + 1 remains within the window.
# At start + 60_001, that request reaches the inclusive removal cutoff.
# Check allowance, count, retry_after, independent keys, and pruning.
# Delete unique test keys and close the Redis client after the check.
# Smolink chooses the exact sliding-window log. It does not use a token bucket.
# See docs/ENGINEERING_PLAYBOOK.md for algorithm comparisons.

import asyncio
from time import time_ns

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.rate_limit import SlidingWindowRateLimiter

def test_sliding_window_enforces_limit_prunes_and_keeps_keys_separate() -> None:
    async def check()->None:
        client =Redis.from_url(get_settings().redis_url)
        limiter=SlidingWindowRateLimiter(client)
        key=f"test:rate:{time_ns()}"
        other_key=f"{key}:other"
        start=1_000_000
        try:
            first=await limiter.check(key,2,60,now_ms=start)
            second = await limiter.check(key, 2, 60, now_ms=start + 1)
            rejected = await limiter.check(key, 2, 60, now_ms=start + 2)
            rejected = await limiter.check(key, 2, 60, now_ms=start + 2)
            other = await limiter.check(other_key, 2, 60, now_ms=start + 2)
            after_window = await limiter.check(key,2,60,now_ms=start + 60_001) 

            assert first.allowed and first.count == 1
            assert second.allowed and second.count == 2
            assert not rejected.allowed
            assert rejected.count == 2
            assert rejected.retry_after == 60
            assert other.allowed and other.count == 1
            assert after_window.allowed and after_window.count == 1
        finally:
            await client.delete(key, other_key)
            await client.aclose()

    asyncio.run(check())
