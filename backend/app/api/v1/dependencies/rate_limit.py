# Guest creation uses rate:create:guest:{ip}, limited to 10 requests per minute.
# User creation uses rate:create:user:{user_id}, limited to 30 per minute.
# Auth POST routes share rate:auth:{ip}, limited to 5 per minute.
# These are rolling 60-second windows, checked atomically in Redis.
# Client IP comes from request.client.host, with "unknown" for no client.
# Invalid Bearer authentication fails before creation limiting continues.
# Denial returns 429. Retry-After is a response header measured in seconds.
# Limiter failure returns 503 because enforcement cannot establish an allowance.
# Inspect exceptions through logs or a debugger. Preserve failure handling.

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.core.rate_limit import SlidingWindowRateLimiter
from app.core.redis import get_redis_client

from app.api.v1.dependencies.auth import get_optional_current_user
from app.models.user import User

async def limit_url_creation(
    request: Request,

    current_user: User | None = Depends(get_optional_current_user),

    client: Redis = Depends(get_redis_client),
) -> None:

    if current_user is None:

        client_ip = (
            request.client.host
            if request.client is not None
            else "unknown"
        )

        key = f"rate:create:guest:{client_ip}"

        limit = 10

    else:

        key = f"rate:create:user:{current_user.id}"

        limit = 30

    try:

        result = await SlidingWindowRateLimiter(client).check(
            key=key,
            limit=limit,
            window_seconds=60,
        )

    except Exception as error:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from error

    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",

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
