# TestClient drives HTTP in process. The database and Redis remain real services.
# The fixture overrides get_session() with a NullPool test engine.
# asyncpg connections belong to their creation loop and cannot cross test loops.
# Each request receives a session. Production pooling remains unchanged.
# FastAPI Depends() records dependency metadata. Overrides replace resolution.
# pytest fixture injection uses the parameter name and resumes cleanup after yield.
# Each request Redis client is created and closed within its TestClient loop.
# Temporary cleanup clients delete fixed limiter keys before and after tests.
# Closing a cleanup client does not stop Redis or close the separate request client.
# Explicit cleanup prevents leaked resources in a long-running process.
# Repository flush() does not commit. A missing route commit rolls back inserts.
# Ownership tests seed a verified user, log in, create a URL, and query owner_id.
# Guest creation stores no owner. Bearer authentication stores the current user's ID.
# Guest and authenticated creation use independent IP and user scopes.
# Ten guest requests pass; the eleventh returns 429 with Retry-After.
# A monkeypatched check() raises OSError to exercise the limiter's 503 policy.
# *args and **kwargs let that replacement accept the original call arguments.
# asyncio.run() bridges synchronous tests and their async setup/inspection helpers.
# See docs/codebase-walkthrough.md for lifecycle and transaction explanations.

from time import time_ns

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.session import get_session
from app.main import app

from datetime import datetime, timedelta, timezone
from app.services.url_service import create_short_url

import asyncio
from redis.asyncio import Redis

from app.core.redis import get_redis_client

from app.models.url import Url
from app.models.user import User
from app.utils.security import hash_password


@pytest.fixture
def client() -> TestClient:
    engine = create_async_engine(
        get_settings().database_url,
        poolclass=NullPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session():
        async with session_factory() as session:
            yield session

    async def override_get_redis_client():
        client = Redis.from_url(get_settings().redis_url)
        try:
            yield client
        finally:
            await client.aclose()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_redis_client] = override_get_redis_client

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    

def test_guest__url_creation_returns_201(client: TestClient)->None:
    response=client.post("/api/v1/urls",
                         json={"destination": "https://example.com"},
    )
    assert response.status_code==201
    assert response.json()["short_code"]
    assert response.json()["short_url"].endswith(f'/{response.json()["short_code"]}')

def test_guest_url_creation_rejects_invalid_destination(client: TestClient) -> None:
    response = client.post(
        "/api/v1/urls",
        json={"destination": "not-a-url"},
    )

    assert response.status_code == 422

def test_guest_url_creation_rejects_duplicate_alias(client: TestClient) -> None:
    alias = f"alias-{time_ns()}"

    first_response = client.post(
        "/api/v1/urls",
        json={"destination": "https://example.com", "alias": alias},
    )
    second_response = client.post(
        "/api/v1/urls",
        json={"destination": "https://example.org", "alias": alias},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "error": "alias_taken",
        "message": "Alias is already taken",
    }
    
def test_guest_url_creation_rejects_past_expiry(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/urls",
        json={
            "destination": "https://example.com",
            "expires_at": (
                datetime.now(timezone.utc) - timedelta(seconds=1)
            ).isoformat(),
        },
    )
    assert response.status_code == 422


def test_guest_url_creation_returns_429_after10_requests(client:TestClient,)->None:
    key="rate:create:guest:testclient" 
    async def clear_limit()->None:
        redis_client=Redis.from_url(get_settings().redis_url)
        try :
            await redis_client.delete(key)
        finally:
            await redis_client.aclose()
    asyncio.run(clear_limit())
    try:
        for i in range(10):
            response=client.post("/api/v1/urls",
                                 json={"destination": "https://example.com"},)
            assert response.status_code==201
        response=client.post("/api/v1/urls", 
                             json={"destination": "https://example.com"},)
        assert response.status_code==429
        assert int(response.headers["Retry-After"])>0
    finally:
        asyncio.run(clear_limit())

def test_guest_url_creation_returns_503_when_limiter_is_unavailable(client: TestClient,monkeypatch: pytest.MonkeyPatch,
                                                                    ) -> None:
    async def unavailable(*args:object, **kwargs:object)->None:
        raise OSError("Redis unavailable")
    monkeypatch.setattr(
    "app.api.v1.dependencies.rate_limit.SlidingWindowRateLimiter.check",
        unavailable,)
    

    response = client.post(
        "/api/v1/urls",
        json={"destination": "https://example.com"},
    )

    assert response.status_code == 503
    

async def seed_verified_user()-> tuple[int, str]:

        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )

        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )

        user_id = time_ns()

        email = f"user-{user_id}@example.com"

        try:
            async with session_factory() as session:

                session.add(
                    User(
                        id=user_id,
                        email=email,
                        password_hash=hash_password("hello12345678"),
                        email_verified_at=datetime.now(timezone.utc),
                    )
                )

                await session.commit()

        finally:
            await engine.dispose()

        return user_id, email


def test_authenticated_url_creation_assigns_owner(
    client: TestClient,
) -> None:

    user_id, email = asyncio.run(seed_verified_user())


    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "hello12345678",
        },
    )

    assert login.status_code == 200


    response = client.post(
        "/api/v1/urls",

        headers={
            "Authorization": f"Bearer {login.json()['access_token']}",
        },

        json={
            "destination": "https://example.com"
        },
    )

    assert response.status_code == 201


    async def load_owner_id() -> int | None:

        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )

        try:
            async with async_sessionmaker(engine)() as session:

                url = await session.get(
                    Url,
                    response.json()["id"],
                )

                assert url is not None

                return url.owner_id

        finally:
            await engine.dispose()


    assert asyncio.run(load_owner_id()) == user_id

def test_authenticated_creation_uses_30_per_user_limit(
        client:TestClient,
)->None:
    user_id, email = asyncio.run(seed_verified_user())

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "hello12345678",
        },
    )
    assert login.status_code == 200

    headers={
        "Authorization":f"Bearer {login.json()["access_token"]}"
    }
    keys = [
        "rate:create:guest:testclient",
        f"rate:create:user:{user_id}",
    ]
    async def clear_limits()->None:
        redis_client=Redis.from_url(get_settings().redis_url)
        try:
            await redis_client.delete(*keys)
        finally:
            await redis_client.aclose()

    asyncio.run(clear_limits())

    try:
        for request_number in range(1, 31):
            response = client.post(
                "/api/v1/urls",
                headers=headers,
                json={"destination": "https://example.com"},
            )
            assert response.status_code == 201, (
                f"request {request_number}: {response.text}"
            )

        response = client.post(
            "/api/v1/urls",
            headers=headers,
            json={"destination": "https://example.com"},
        )

        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) > 0
    finally:
        asyncio.run(clear_limits())
