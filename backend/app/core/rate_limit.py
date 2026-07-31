#The window is recomputed on every request.
import math
import time
from dataclasses import dataclass
from uuid import uuid4

from redis.asyncio import Redis

SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]
local cutoff = now - window

redis.call("ZREMRANGEBYSCORE", key, 0, cutoff)

local count = redis.call("ZCARD", key)

if count >= limit then
    local oldest = redis.call("ZRANGE", key, 0, 0, "WITHSCORES")[2]
    return {0, count, oldest}
end

redis.call("ZADD", key, now, member)
redis.call("PEXPIRE", key, window)

return {1, count + 1, 0}
"""
# Immutable value object representing the outcome of a rate-limit check.
# @dataclass automatically generates __init__, __repr__, and __eq__,
# while frozen=True prevents the result from being modified after creation.
@dataclass(frozen=True)
class RateLimitResult:
    allowed:bool
    count:int
    retry_after:int
class SlidingWindowRateLimiter:
    def __init__(self,client:Redis):
        self._client=client

    async def check( self , key:str, limit:int, window_seconds:int, now_ms:int|None=None,
                    )-> RateLimitResult:
        current_ms= (now_ms if now_ms is not None else time.time_ns()//1000000) #bcz ns to ms
        #Default arguments in Python are evaluated once, when the function is defined, not every time it's called.
        window_ms=window_seconds*1000
        allowed,count,oldest=await self._client.eval(
            SLIDING_WINDOW_SCRIPT,
            1,
            key,
            current_ms,
            window_ms,
            limit,
            f"{current_ms}:{uuid4().hex}",
        )

        if allowed==1:
            return RateLimitResult(
                allowed=True,
                count=int(count),
                retry_after=0,
            )
        retry_after=max(1,math.ceil((int(oldest)+window_ms-current_ms)/1000))

        return RateLimitResult(allowed=False,
                               count=int(count),
                               retry_after=retry_after)


# Remove all requests that have fallen outside the sliding window, then count
# the remaining requests. If the limit has already been reached, retrieve the
# oldest request's timestamp and return it so the caller can calculate how
# long the client must wait before retrying. Otherwise, record the current
# request, reset the key's expiration time to automatically clean up inactive
# rate-limit entries, and return a successful result with the updated request
# count.


# -----------------------------------------------------------------------------
# Sliding Window Rate Limiter
#
# This module implements a Redis-backed sliding window rate limiter using a
# Redis Sorted Set (ZSET). Each incoming request is stored with its timestamp
# as the score and a unique member value. Before processing a new request, all
# timestamps outside the configured time window are removed, ensuring that only
# recent requests are counted.
#
# The core rate-limiting logic is implemented as a Lua script and executed
# atomically inside Redis using EVAL. Performing pruning, counting, checking
# the limit, and inserting the new request in a single Redis operation prevents
# race conditions that could occur if multiple clients updated the same key
# simultaneously.
#
# Each Redis key represents an independent rate limit (for example, a user,
# client IP, or API key). Expired request timestamps are pruned on every
# request using ZREMRANGEBYSCORE, while PEXPIRE automatically removes inactive
# keys after an entire window has passed, preventing Redis from accumulating
# empty Sorted Sets.
#
# The check() method returns a RateLimitResult indicating whether the request
# is allowed, the number of requests currently within the sliding window, and
# the number of seconds the client should wait before retrying when the limit
# is exceeded.
# -----------------------------------------------------------------------------

# Client
#    │
#    ▼
# check(key, limit, window)
#    │
#    ▼
# Determine current time
#    │
#    ▼
# Call Redis Lua script
#    │
#    ▼
# Lua:
#    │
#    ├── Remove expired timestamps
#    ├── Count remaining requests
#    ├── Is limit reached?
#    │      │
#    │      ├── Yes → Return oldest timestamp
#    │      │
#    │      └── No → Add request + refresh TTL
#    │
#    ▼
# Python receives (allowed, count, oldest)
#    │
#    ├── Allowed → return RateLimitResult
#    │
#    └── Rejected → compute Retry-After → return RateLimitResult