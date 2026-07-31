from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.core.rate_limit import SlidingWindowRateLimiter
from app.core.redis import get_redis_client


async def limit_guest_creation(
    request: Request,
    client: Redis = Depends(get_redis_client),
) -> None:
    client_ip = request.client.host if request.client is not None else "unknown"

    try:
        result = await SlidingWindowRateLimiter(client).check(
            f"rate:create:guest:{client_ip}",
            10,
            60,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from error

    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(result.retry_after)},
        )

#A FastAPI dependency that runs before an endpoint.
#==========================================================================================
#whenever errors remove teh try except block to inspect proper error codes
#==========================================================================================
# HTTP responses are divided into:
#   1. Status code  -> what happened (e.g., 429 Too Many Requests)
#   2. Headers      -> protocol metadata (e.g., Retry-After, Content-Type)
#   3. Body         -> application data or error details
#
# Retry-After is a standard HTTP response header, not part of the JSON body.
# It tells clients how many seconds to wait before retrying, allowing generic
# HTTP clients, SDKs, proxies, and browsers to handle rate limiting without
# needing to understand the API's custom response format.
#
# Example:
#   HTTP/1.1 429 Too Many Requests
#   Retry-After: 42
#
#   {
#       "detail": "Rate limit exceeded"
#   }

#==========================================================================================

# The rate-limiting dependency depends on Redis. If Redis is unavailable or an
# unexpected error occurs while checking the limit, the service cannot determine
# whether the request should be allowed. In that case, we return HTTP 503
# (Service Unavailable) instead of exposing internal errors (500) or returning
# an incorrect rate-limiting decision.
#
# During debugging, temporarily remove the broad try/except block. This allows
# the original exception and traceback to propagate, making it much easier to
# identify the real cause (e.g., Redis connection failure, event-loop mismatch,
# Lua script error, etc.). Once the issue is fixed, restore the exception
# handling so production clients consistently receive a 503 response instead of
# internal implementation details.