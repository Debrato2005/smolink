import asyncio
from time import time_ns

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.rate_limit import SlidingWindowRateLimiter

def test_sliding_window_enforces_limit_prunes_and_keeps_keys_separate() -> None:
    async def check()->None: #Because without plugins like pytest-asyncio, pytest expects normal functions.
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
#use start + 60_001, not start + 60_000.
#At exactly 60 seconds, the request made at start + 1ms is still inside the rolling window.

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
# Rate Limiting Algorithms:
#
#Fixed Window
#- Uses a single counter for each fixed time window (e.g., 100 requests/minute).
#- Pros: Simplest implementation, O(1) operations, minimal Redis memory.
#- Cons: Suffers from boundary bursts (e.g., 100 requests at 12:00:59 + 100 at 12:01:00).
#
#Sliding Window Log
#- Stores a timestamp for every request and counts only those within the rolling window.
#- Pros: Most accurate and fair; completely eliminates boundary bursts.
#- Cons: Highest Redis memory and CPU usage due to per-request timestamp storage.
#
#Sliding Window Counter
#- Maintains counters for the current and previous windows, weighting the previous
#  window based on elapsed time to approximate a true sliding window.
#- Pros: Good balance between fairness and efficiency; much lower Redis overhead
#  than the log approach.
#- Cons: Approximation, not perfectly accurate.
#
#Token Bucket (Recommended)
#- Tokens are added to a bucket at a fixed rate; each request consumes one token.
#- Pros: O(1), low Redis overhead, supports short bursts while enforcing a long-term
#  average rate, and is widely used in production API gateways.
#- Cons: Slightly more complex than fixed/sliding counters due to refill calculations.
#
#Leaky Bucket
#- Requests are queued and processed at a constant rate, regardless of arrival bursts.
#- Pros: Produces smooth, predictable traffic and protects downstream services.
#- Cons: Can increase request latency due to queuing; better suited for traffic shaping
#  than interactive APIs.
#------------------------------------------------------------------------------------------
# Fixed Window vs Sliding Window test differences
#
# Fixed Window:
# - Checks Redis TTL is created (window reset is handled by key expiration).
# - Uses the real clock; no time injection needed.
# - Verifies the counter keeps incrementing, even for rejected requests.
# - Focuses on counter, TTL, retry_after, and key isolation.
#
# Sliding Window:
# - Injects a fake clock (now_ms) for deterministic testing.
# - Verifies expired timestamps are pruned when the window moves.
# - Checks the count only includes requests inside the current window.
# - Focuses on pruning logic, retry_after, and key isolation instead of TTL.
#
# #------------------------------------------------------------------------------------------
#
# Test flow:
# 1. Connect to Redis and create the SlidingWindowRateLimiter.
# 2. Create unique Redis keys to avoid collisions with other test runs.
# 3. Simulate requests using a fake clock (now_ms):
#    - Request 1 -> allowed (count = 1)
#    - Request 2 -> allowed (count = 2)
#    - Request 3 -> rejected (limit reached)
#    - Different key -> allowed (independent rate limit)
#    - Advance time by one window -> old timestamps are pruned,
#      so the next request is allowed again (count = 1).
# 4. Verify counts, retry_after, key isolation, and pruning behavior.
# 5. Delete test keys and close the Redis connection.
#
#------------------------------------------------------------------------------------------
#
# Why asyncio.run(check())?
#
# - The test itself is synchronous (def test_...), but the code under test
#   is asynchronous (await limiter.check(...)).
# - asyncio.run() creates a temporary event loop, runs check() to completion,
#   then automatically closes the loop.
# - It does NOT affect FastAPI/Uvicorn's event loop because this test is
#   running independently, not inside a running async application.
# - Do NOT call asyncio.run() from inside an already running event loop
#   (e.g., inside an async function or FastAPI endpoint); it will raise
#   RuntimeError: asyncio.run() cannot be called from a running event loop.
# - If using pytest-asyncio, write `async def test_...` instead and let
#   pytest manage the event loop.
#
#------------------------------------------------------------------------------------------
#
# This test verifies that:
# - A single key is limited to 2 requests per 60-second sliding window.
# - Requests beyond the limit are rejected and include a retry_after value.
# - Each Redis key has an independent rate limit (one key being blocked
#   does not affect another key).
# - After the window expires, old request timestamps are pruned, allowing
#   the key to make requests again.
# - Redis state is cleaned up after the test.