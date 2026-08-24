from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.core.rate_limit import SlidingWindowRateLimiter
from app.core.redis import get_redis_client

from app.api.v1.dependencies.auth import get_optional_current_user
from app.models.user import User

async def limit_url_creation(
    request: Request,

    # Optional authentication:
    #
    # - no Bearer token  -> current_user = None
    # - valid Bearer token -> current_user = User(...)
    # - invalid Bearer token -> 401 before this limiter continues
    #
    # We need this because URL creation supports BOTH guests and logged-in users.
    current_user: User | None = Depends(get_optional_current_user),

    # Redis stores the rate-limit counters.
    # FastAPI injects the Redis client through get_redis_client().
    client: Redis = Depends(get_redis_client),
) -> None:

    # Decide WHICH rate-limit bucket this request belongs to.
    if current_user is None:

        # Guest users do not have a user ID, so rate-limit them by IP address.
        #
        # Example:
        #     request.client.host == "192.168.1.10"
        #
        # In TestClient this is usually:
        #     "testclient"
        client_ip = (
            request.client.host
            if request.client is not None
            else "unknown"
        )

        # Each guest IP gets its own Redis key.
        #
        # Example:
        #     rate:create:guest:192.168.1.10
        #
        # Therefore requests from one guest IP increment the same counter.
        key = f"rate:create:guest:{client_ip}"

        # Guests may create at most 10 URLs within the rate-limit window.
        limit = 10

    else:

        # Logged-in users have a stable database user ID,
        # so rate-limit by user ID instead of IP.
        #
        # Example:
        #     user.id == 123
        #
        # Redis key:
        #     rate:create:user:123
        #
        # This means the same account gets the same rate-limit bucket
        # even if its IP address changes.
        key = f"rate:create:user:{current_user.id}"

        # Authenticated users receive a larger allowance.
        limit = 30

    try:

        # Check/update the sliding-window counter in Redis.
        #
        # `key` decides WHO is being limited:
        #
        #     guest -> rate:create:guest:<ip>
        #     user  -> rate:create:user:<user_id>
        #
        # `limit` decides HOW MANY requests are allowed:
        #
        #     guest -> 10
        #     user  -> 30
        #
        # `window_seconds=60` means these limits apply over a 60-second window.
        result = await SlidingWindowRateLimiter(client).check(
            key=key,
            limit=limit,
            window_seconds=60,
        )

    except Exception as error:

        # If Redis/rate limiting itself fails, we cannot safely determine
        # whether the request should be allowed.
        #
        # Return 503 Service Unavailable instead of pretending the user is
        # under/over the limit or exposing an internal exception.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from error

    # The limiter returns a RateLimitResult.
    #
    # result.allowed == True
    #     -> dependency returns normally
    #     -> FastAPI proceeds to the /urls endpoint
    #
    # result.allowed == False
    #     -> reject the request with HTTP 429
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",

            # Tell the client approximately how many seconds it should wait
            # before retrying.
            headers={
                "Retry-After": str(result.retry_after)
            },
        )
async def limit_auth_write(request:Request, client: Redis=Depends(get_redis_client),
                           )->None:
    
    client_ip=request.client.host if request.client is not None else "unknown"

    try :
        result = await SlidingWindowRateLimiter(client).check(
            f"rate:auth:{client_ip}",
            5,
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