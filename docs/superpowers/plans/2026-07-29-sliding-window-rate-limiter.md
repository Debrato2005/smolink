# Sliding-window rate limiter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce fair rolling-minute limits for guest URL creation with Redis and prepare reusable policies for auth.

**Architecture:** A Lua script owns every sorted-set mutation so concurrent requests cannot exceed a limit. A small FastAPI dependency selects an IP-scoped key for guest creation and translates a Redis outage into `503`; the URL endpoint receives `429` with `Retry-After` when the script denies a request.

**Tech Stack:** Python 3.13, FastAPI, redis-py async client, Redis Lua, pytest.

## Global Constraints

- Postgres remains authoritative; Redis rate-limit keys are ephemeral enforcement data.
- Sliding windows are exact rolling 60-second windows, not fixed buckets.
- `/health` and redirects remain un-limited.
- Redis failures on protected writes fail closed with `503`.
- Use `uv run pytest -q -s`; do not change the production SQLAlchemy pool for tests.

---

### Task 1: Sliding-window Redis primitive

**Files:**
- Create: `backend/app/core/rate_limit.py`
- Modify: `backend/tests/test_rate_limiter.py`

**Produces:** `SlidingWindowRateLimiter.check(key, limit, window_seconds, now_ms=None)` returning a `RateLimitResult` with `allowed`, `count`, and `retry_after`.

- [ ] **Step 1: Replace the red test with deterministic rolling-window checks**

```python
import asyncio
from time import time_ns

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.rate_limit import SlidingWindowRateLimiter


def test_sliding_window_enforces_limit_prunes_and_keeps_keys_separate() -> None:
    async def check() -> None:
        client = Redis.from_url(get_settings().redis_url)
        limiter = SlidingWindowRateLimiter(client)
        key = f"test:rate:{time_ns()}"
        other_key = f"{key}:other"
        start = 1_000_000

        try:
            first = await limiter.check(key, 2, 60, now_ms=start)
            second = await limiter.check(key, 2, 60, now_ms=start + 1)
            rejected = await limiter.check(key, 2, 60, now_ms=start + 2)
            other = await limiter.check(other_key, 2, 60, now_ms=start + 2)
            after_window = await limiter.check(key, 2, 60, now_ms=start + 60_000)

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
```

- [ ] **Step 2: Run the red test**

Run: `uv run pytest tests/test_rate_limiter.py -q -s`  
Expected: import failure for `SlidingWindowRateLimiter`.

- [ ] **Step 3: Implement the Lua-backed primitive**

```python
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
redis.call('ZREMRANGEBYSCORE', key, 0, cutoff)
local count = redis.call('ZCARD', key)
if count >= limit then
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')[2]
    return {0, count, oldest}
end
redis.call('ZADD', key, now, member)
redis.call('PEXPIRE', key, window)
return {1, count + 1, 0}
"""


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    count: int
    retry_after: int


class SlidingWindowRateLimiter:
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def check(
        self, key: str, limit: int, window_seconds: int, now_ms: int | None = None
    ) -> RateLimitResult:
        current_ms = now_ms or time.time_ns() // 1_000_000
        window_ms = window_seconds * 1_000
        allowed, count, oldest = await self._client.eval(
            SLIDING_WINDOW_SCRIPT,
            1,
            key,
            current_ms,
            window_ms,
            limit,
            f"{current_ms}:{uuid4().hex}",
        )
        if allowed == 1:
            return RateLimitResult(True, int(count), 0)
        retry_after = max(1, math.ceil((int(oldest) + window_ms - current_ms) / 1_000))
        return RateLimitResult(False, int(count), retry_after)
```

- [ ] **Step 4: Run the green test**

Run: `uv run pytest tests/test_rate_limiter.py -q -s`  
Expected: `1 passed`.

### Task 2: Guest-creation FastAPI dependency

**Files:**
- Create: `backend/app/core/redis.py`
- Create: `backend/app/api/v1/dependencies/rate_limit.py`
- Modify: `backend/app/api/v1/endpoints/urls.py`
- Modify: `backend/tests/test_url_creation.py`

**Consumes:** `SlidingWindowRateLimiter.check(...)`.
**Produces:** a dependency that permits at most 10 guest creations per request-client IP per rolling minute.

- [ ] **Step 1: Add endpoint expectations**

```python
def test_guest_url_creation_returns_429_after_ten_requests(client: TestClient) -> None:
    for _ in range(10):
        assert client.post("/api/v1/urls", json={"destination": "https://example.com"}).status_code == 201

    response = client.post("/api/v1/urls", json={"destination": "https://example.com"})

    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
```

- [ ] **Step 2: Run the red endpoint test**

Run: `uv run pytest tests/test_url_creation.py -q -s`  
Expected: the eleventh request returns `201`.

- [ ] **Step 3: Add Redis client, dependency, and route parameter**

```python
# app/core/redis.py
from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> Redis:
    return Redis.from_url(get_settings().redis_url)
```

```python
# app/api/v1/dependencies/rate_limit.py
from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.core.redis import get_redis_client
from app.core.rate_limit import SlidingWindowRateLimiter


async def limit_guest_creation(
    request: Request,
    client: Redis = Depends(get_redis_client),
) -> None:
    client_ip = request.client.host if request.client is not None else "unknown"
    try:
        result = await SlidingWindowRateLimiter(client).check(
            f"rate:create:guest:{client_ip}", 10, 60
        )
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE) from error
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(result.retry_after)},
        )
```

```python
# add to the URL route imports and signature
from app.api.v1.dependencies.rate_limit import limit_guest_creation

async def create_url(
    payload: CreateUrlRequest,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(limit_guest_creation),
) -> CreateUrlResponse | JSONResponse:
```

- [ ] **Step 4: Run the endpoint test**

Run: `uv run pytest tests/test_url_creation.py -q -s`  
Expected: creation requests 1–10 return `201`; request 11 returns `429` with `Retry-After`.

### Task 3: Redis outage contract and documentation

**Files:**
- Modify: `backend/tests/test_url_creation.py`
- Modify: `docs/backend-build-checklist.md`
- Modify: `docs/codebase-walkthrough.md`

- [ ] **Step 1: Add a failing Redis-outage test**

```python
def test_guest_url_creation_returns_503_when_limiter_is_unavailable(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def unavailable(*args: object, **kwargs: object) -> None:
        raise OSError("Redis unavailable")

    monkeypatch.setattr(
        "app.api.v1.dependencies.rate_limit.SlidingWindowRateLimiter.check",
        unavailable,
    )

    response = client.post("/api/v1/urls", json={"destination": "https://example.com"})

    assert response.status_code == 503
```

- [ ] **Step 2: Run the test and document verified behavior**

Run: `uv run pytest tests/test_rate_limiter.py tests/test_url_creation.py -q -s`  
Expected: all tests pass; only rate-limited writes fail closed when Redis is unavailable.
