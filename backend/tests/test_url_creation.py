from time import time_ns

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.session import get_session
from app.main import app

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

    app.dependency_overrides[get_session] = override_get_session

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