# Redis EVAL makes pruning, counting, allowance, insertion, and expiry atomic.
# Sorted-set members combine a timestamp and UUID. Scores are milliseconds.
# Scores through the cutoff are removed before counting.
# Allowed requests reset PEXPIRE. Rejected requests do not add a member.
# check() returns allowed, count, and retry_after in a frozen dataclass.
# Dataclasses generate initialization, representation, and equality methods.
# frozen=True prevents normal attribute assignment after creation.
# An explicit now_ms enables deterministic tests, including a zero timestamp.
# Denied retry time rounds upward to seconds, with a minimum of one second.

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
        current_ms= (now_ms if now_ms is not None else time.time_ns()//1000000)
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
