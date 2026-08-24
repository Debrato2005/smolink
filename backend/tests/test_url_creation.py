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

#TestClient does not create a fake database. It only creates a fake HTTP client.

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


#endpoint rate limit test
def test_guest_url_creation_returns_429_after10_requests(client:TestClient,)->None:
    key="rate:create:guest:testclient" 
    async def clear_limit()->None:
        redis_client=Redis.from_url(get_settings().redis_url) #This client exists only to delete the key before and after the test.
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

#redis outage test
def test_guest_url_creation_returns_503_when_limiter_is_unavailable(client: TestClient,monkeypatch: pytest.MonkeyPatch,
                                                                    ) -> None:
    async def unavailable(*args:object, **kwargs:object)->None: #Accept any positional or keyword arguments
        raise OSError("Redis unavailable") #OSError is a built-in Python exception used when an operating system or external resource fails.
    #can use Exception. The test would still work.
    monkeypatch.setattr(
    "app.api.v1.dependencies.rate_limit.SlidingWindowRateLimiter.check",
        unavailable,)
    
# Temporarily replace the Redis-backed rate limiter's `check()` method with the
# test's `unavailable()` function. This simulates Redis being unavailable
# without stopping the real Redis server, allowing us to verify that the
# application handles rate-limiter failures correctly.

    response = client.post(
        "/api/v1/urls",
        json={"destination": "https://example.com"},
    )

    assert response.status_code == 503
    
# Monkeypatch temporarily replaces SlidingWindowRateLimiter.check() with a fake
# implementation that always raises OSError, simulating Redis or rate-limiter
# failure. This verifies that the dependency converts unexpected internal
# errors into HTTP 503 Service Unavailable instead of exposing the exception
# or crashing the application.

#SEED USER outside now so that other functions can use it as well
# Helper used only to create the prerequisite test user directly in the DB.
# We seed the user instead of registering through the API because this test
 # is about URL ownership, not registration/email-verification behavior.
async def seed_verified_user()-> tuple[int, str]:

        # Create a temporary async SQLAlchemy engine connected to the test DB.
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )

        # Create a factory that can generate AsyncSession objects.
        # expire_on_commit=False keeps ORM object attributes available after commit.
        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )

        # Generate a unique user ID so this test is unlikely to collide
        # with users created by other tests.
        user_id = time_ns()

        # Create a unique email for the same reason.
        email = f"user-{user_id}@example.com"

        try:
            # Open a temporary database session.
            async with session_factory() as session:

                # Create an already-verified user directly in PostgreSQL.
                # email_verified_at is set so this user is allowed to log in.
                session.add(
                    User(
                        id=user_id,
                        email=email,
                        password_hash=hash_password("hello12345678"),
                        email_verified_at=datetime.now(timezone.utc),
                    )
                )

                # Persist the seeded user so the later TestClient request,
                # which uses a different DB session, can see this user.
                await session.commit()

        finally:
            # Dispose of the temporary database engine even if an error occurs.
            await engine.dispose()

        # Return the values needed by the synchronous part of the test.
        return user_id, email


def test_authenticated_url_creation_assigns_owner(
    client: TestClient,
) -> None:

    # seed_user() is async, but the test itself is synchronous.
    # asyncio.run() creates an event loop, executes the helper,
    # and gives us back the created user's ID and email.
    user_id, email = asyncio.run(seed_verified_user())


    # Log in normally through the real /login endpoint.
    # This tests the actual authentication flow rather than manually creating a JWT.
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "hello12345678",
        },
    )

    # Make sure login succeeded before continuing.
    assert login.status_code == 200


    # Create a URL while acting as the logged-in user.
    response = client.post(
        "/api/v1/urls",

        # Login returned an access JWT.
        # The client sends it using the standard HTTP Authorization header:
        #
        # Authorization: Bearer <access_token>
        #
        # FastAPI's OAuth2PasswordBearer extracts this token, and the backend
        # validates it to determine which user is making the request.
        headers={
            "Authorization": f"Bearer {login.json()['access_token']}",
        },

        # Request body for URL creation.
        json={
            "destination": "https://example.com"
        },
    )

    # Confirm that the URL was created successfully.
    assert response.status_code == 201


    # We now want to verify something that is not necessarily visible in the
    # API response: the database URL row's owner_id.
    #
    # Because this test function is synchronous but SQLAlchemy DB operations
    # are async, we wrap the DB query inside another async helper.
    async def load_owner_id() -> int | None:

        # Create another temporary async DB engine.
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )

        try:
            # Create and open an AsyncSession.
            async with async_sessionmaker(engine)() as session:

                # response.json() converts the /urls JSON response into
                # a Python dictionary.
                #
                # ["id"] gets the ID of the URL that was just created.
                #
                # session.get(Url, id) loads that exact URL row from PostgreSQL
                # using its primary key.
                url = await session.get(
                    Url,
                    response.json()["id"],
                )

                # If the API returned 201 but somehow no DB row exists,
                # fail the test immediately instead of accessing None.owner_id.
                assert url is not None

                # Return the owner_id stored on the URL row.
                return url.owner_id

        finally:
            # Always close/dispose the temporary DB engine.
            await engine.dispose()


    # Run the async DB helper from this synchronous test.
    #
    # Then check that:
    #
    # URL.owner_id == ID of the user who logged in
    #
    # This proves authenticated URL creation correctly associates
    # the newly created URL with its authenticated owner.
    assert asyncio.run(load_owner_id()) == user_id
    # Authenticated URL ownership flow:
#
# Goal:
# - Guests can still create URLs.
# - Logged-in users can create URLs that are linked to their account.
#
# The ownership test:
# 1. Seeds a verified user in the DB.
# 2. Logs in and gets an access token.
# 3. Sends:
#       Authorization: Bearer <access_token>
#    when creating the URL.
# 4. Loads that URL directly from PostgreSQL.
# 5. Checks:
#       url.owner_id == logged_in_user.id
#
# The test originally failed because /urls always used:
#       owner_id=None
# so every URL was stored as anonymous even when a valid token was sent.
#
# We cannot simply use Depends(get_current_user) on /urls because that would
# make authentication mandatory and break guest URL creation.
#
# Therefore we add optional authentication:
#
# optional_oauth2_scheme = OAuth2PasswordBearer(..., auto_error=False)
#
# auto_error=False means:
#   no Authorization header -> token=None instead of automatic 401
#
# get_optional_current_user() then behaves as:
#   no token      -> return None          (guest)
#   valid token   -> get_current_user() -> User
#   invalid token -> get_current_user() -> 401
#
# /urls receives:
#   current_user: User | None = Depends(get_optional_current_user)
#
# Then ownership is assigned with:
#   owner_id = current_user.id if current_user is not None else None
#
# Therefore:
#   guest request      -> owner_id=None
#   authenticated user -> owner_id=user.id
#
# This change only completes URL ownership.
#
# Rate limiting is still using limit_guest_creation for everyone.
# Next step:
#   guest             -> rate limit by IP
#   authenticated user -> rate limit by user ID
#############################################################################################################################

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
# Why the "different event loop" error happened
#
# - `engine = create_async_engine(...)` is a global object, created once when
#   `app.db.session` is imported.
#
# - The Engine owns a connection pool. Since the Engine is global, the pool is
#   also global and shared by everyone using that Engine.
#
# - In production, this is fine because Uvicorn runs the application on a
#   stable event loop for the lifetime of the worker process. All pooled
#   connections are created and reused on that same loop.
#
#       Uvicorn
#          │
#     Event Loop A
#          │
#     Global Engine
#          │
#     Global Pool
#          │
#   Request 1, Request 2, Request 3 ...
#
# - During testing, different tests may run on different event loops.
#   Example:
#
#       test_db_session.py  -> asyncio.run()  -> Event Loop A
#       test_url_creation.py -> TestClient    -> Event Loop B
#
# - Both tests import the same global Engine, so they also share the same pool.
#   The pool may return a connection created on Loop A to code running on
#   Loop B.
#
# - asyncpg binds each connection to the event loop that created it.
#   Reusing that connection from another loop raises:
#
#       RuntimeError: Future attached to a different loop
#
# - The fix is NOT to change production to NullPool.
#
# - Instead, API integration tests override `get_session()` with a temporary
#   Engine using `NullPool`. NullPool never reuses connections:
#
#       Create connection
#            ↓
#         Use it
#            ↓
#       Close it immediately
#
# - Therefore every test gets a fresh connection created on the current event
#   loop, eliminating cross-loop reuse while leaving the production pooled
#   Engine unchanged.



# =============================================================================
# Test Fixture Notes
# =============================================================================
#
# Why this fixture exists
# -----------------------
# Production uses one global SQLAlchemy Engine and connection pool.
# During tests, multiple event loops may exist (asyncio.run(), TestClient,
# pytest-asyncio, etc.). asyncpg connections are bound to the event loop that
# created them, so reusing pooled connections across loops causes:
#
#     RuntimeError: Future attached to a different loop
#
# Example:
#
#     test_db_session.py      -> asyncio.run() -> Event Loop A
#     test_url_creation.py    -> TestClient    -> Event Loop B
#
# Both import the same global Engine:
#
#     Global Engine
#          │
#     Global Pool
#      ├──────── Connection created on Loop A
#      └──────── Reused on Loop B  ❌
#
# asyncpg rejects this because each connection belongs to exactly one event
# loop.
#
# Production is NOT broken
# ------------------------
# Uvicorn workers normally run on one stable event loop:
#
#     Uvicorn Worker
#          │
#      Event Loop A
#          │
#     Global Engine
#          │
#      Global Pool
#          │
#   Request 1 → Request 2 → Request 3
#
# Connections are created and reused on the same loop, so pooling works
# correctly.
#
# Test Solution
# -------------
# Do NOT modify the production Engine.
#
# Instead this fixture:
#
# 1. Creates a temporary Engine.
# 2. Uses poolclass=NullPool.
# 3. Creates a temporary async_sessionmaker.
# 4. Overrides FastAPI's get_session dependency.
# 5. Removes the override after the test.
#
# NullPool disables connection reuse:
#
#     Create Connection
#            │
#         Use It
#            │
#       Close Immediately
#
# Every request receives a brand-new connection created on the current event
# loop, eliminating cross-loop reuse.
#
# FastAPI Dependency Override
# ---------------------------
# app.dependency_overrides is NOT a function.
#
# It is a built-in FastAPI dictionary:
#
#     {
#         original_dependency : replacement_dependency
#     }
#
# Example:
#
#     app.dependency_overrides[get_session] = override_get_session
#
# During dependency resolution FastAPI conceptually does:
#
#     dependency = get_session
#
#     if dependency in app.dependency_overrides:
#         dependency = app.dependency_overrides[dependency]
#
#     session = await dependency()
#
# After the test:
#
#     app.dependency_overrides.clear()
#
# restores normal production behavior.
#
# Why Depends(get_session)?
# -------------------------
# Depends() does NOT call get_session().
#
# It creates metadata telling FastAPI:
#
#     "Before running this endpoint, resolve this dependency and inject it."
#
# Endpoint:
#
#     session: AsyncSession = Depends(get_session)
#
# Production:
#
#     Endpoint
#        │
#     Depends(get_session)
#        │
#     get_session()
#        │
#     Production DB
#
# Tests:
#
#     Endpoint
#        │
#     Depends(get_session)
#        │
#     override_get_session()
#        │
#     Test Engine
#
# Because the endpoint never directly calls get_session(), FastAPI can replace
# it without changing endpoint code.
#
# Pytest Fixture Injection
# ------------------------
# client is passed as a test parameter because it is a pytest fixture.
#
# Example:
#
#     def test_create_url(client):
#
# pytest sees "client", executes the fixture, and passes its returned
# TestClient into the test automatically.
#
# This is dependency injection by pytest (different from FastAPI's dependency
# injection).
#
# Transaction Reminder
# --------------------
# get_session() only yields a session; it does NOT commit automatically.
#
# Repository:
#
#     session.add(...)
#     await session.flush()
#
# flush() writes SQL inside the current transaction but does NOT permanently
# save it.
#
# Without:
#
#     await session.commit()
#
# the session closes at request end and SQLAlchemy rolls back the transaction.
#
# Therefore the endpoint is the correct transaction boundary:
#
#     Repository -> DB operations
#     Service    -> Business logic
#     Endpoint   -> commit()/rollback()
#
# A missing commit caused duplicate-alias tests to behave like:
#
#     Request 1
#         INSERT
#         flush()
#         Session closes
#         ROLLBACK
#
#     Request 2
#         Database appears empty
#         INSERT succeeds again
#
# Fix:
#
#     url = await create_short_url(...)
#     await session.commit()
#
# Key Takeaways
# -------------
# • Global Engine ⇒ Global Pool.
# • asyncpg connections are bound to one event loop.
# • NullPool avoids cross-loop connection reuse in tests.
# • Keep pooled Engine in production.
# • app.dependency_overrides is a FastAPI dictionary, not a function.
# • Depends() is metadata; FastAPI performs dependency injection.
# • pytest fixtures inject objects into tests.
# • Endpoint owns transaction commit/rollback.
# =============================================================================
# =============================================================================
# Why override get_redis_client() in tests?
#
# The production app uses a cached Redis client:
#
#     @lru_cache
#     def get_redis_client():
#         return Redis.from_url(...)
#
# This is fine in production because FastAPI runs on one long-lived event loop,
# so the same Redis client is reused safely for the lifetime of the application.
#
# In the test suite, however, each TestClient creates its own asyncio event loop.
#
# Test 1:
#     Event Loop A
#         └── cached Redis client is created
#
# Test 2:
#     Event Loop B
#         └── get_redis_client() returns the SAME cached client
#
# The cached Redis client still belongs to Event Loop A, so using it from
# Event Loop B raises errors such as:
#
#     RuntimeError: Future attached to a different loop
#     RuntimeError: Event loop is closed
#
# To keep tests isolated, we override get_redis_client() so that each TestClient
# receives a fresh Redis client tied to its own event loop. The client is closed
# after the test finishes, preventing cross-test event loop issues.
# =============================================================================
# =============================================================================

# Resource cleanup summary
#
# 1. Use try...finally only when something MUST be cleaned up.
#
# Pattern:
#
#     resource = acquire()
#     try:
#         use(resource)
#     finally:
#         release(resource)
#
# Examples:
#   - close file
#   - close Redis/DB connection
#   - release a lock
#   - delete temporary test data
#
# If there is nothing to clean up, a try...finally block is unnecessary.
#
# Redis clients
# -------------
# There are TWO different Redis clients in the rate-limit test.
#
# (1) Test Redis client
#
#     redis_client = Redis.from_url(...)
#
# Purpose:
#   - delete the rate-limit key before the test
#   - delete it again after the test
#
# It is closed immediately with:
#
#     await redis_client.aclose()
#
# Closing this client only closes THAT connection.
#
# (2) Application Redis client
#
#     TestClient
#         │
#         ▼
#     FastAPI
#         │
#     App Redis Client
#         │
#         ▼
#     Redis Server
#
# This is the client FastAPI uses internally during:
#
#     client.post("/api/v1/urls")
#
# It is completely independent of the temporary test client.
#
# Therefore:
#
#     await redis_client.aclose()
#
# DOES NOT stop Redis.
# DOES NOT stop FastAPI.
# DOES NOT affect the application's Redis connection.
#
# It only closes the temporary connection used for cleanup.
#
# What happens if you don't close it?
# -----------------------------------
#
# Short-lived script:
#   Usually nothing noticeable. When the process exits (or the PC restarts),
#   the operating system closes all remaining connections.
#
# Long-running application:
#   Open connections accumulate, eventually exhausting available resources.
#   This is why production code always performs explicit cleanup instead of
#   relying on process termination or a system reboot.
#
# Test flow
# ---------
#
# 1. Create temporary Redis client
# 2. Delete old rate-limit key
# 3. Close temporary Redis client
# 4. Send 10 POST requests (FastAPI uses its OWN Redis client)
# 5. 11th request returns 429
# 6. Create temporary Redis client again
# 7. Delete test key
# 8. Close temporary Redis client