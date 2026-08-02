from collections.abc import AsyncGenerator
from time import time_ns

import pytest
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.redis import get_redis_client
from app.db.session import get_session
from app.main import app

@pytest.fixture
def client()->TestClient:
    engine=create_async_engine(get_settings().database_url,
                               poolclass=NullPool,)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
# Keep ORM objects usable after commit by preventing SQLAlchemy from
# expiring their attributes. This avoids automatic database reloads when
# accessing fields after commit, which is especially convenient in async
# applications and tests where the session may no longer be active.
    async def override_get_session()-> AsyncGenerator:
        async with session_factory() as session:
            yield session

    async def override_get_redis_client() -> AsyncGenerator[Redis, None]:
        redis_client = Redis.from_url(get_settings().redis_url)

        try:
            yield redis_client
        finally:
            await redis_client.aclose()
#dependency_overrides is a dictionary.
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_redis_client] = override_get_redis_client

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_register_creates_user_without_exposing_password(client:TestClient)->None:
    email=f"agent-{time_ns()}@example.com"
    response=client.post("/api/v1/auth/register", 
                         json={
                             "email": email,
                             "password":"hello12345678"
                         },
                         )
    assert response.status_code==201
    body=response.json()
    assert isinstance(body["id"],int)
#isinstance() is a built-in Python function that checks whether an object is of a particular type (or class).
    assert body["email"] == email
    assert "created_at" in body
    assert "password" not in body
    assert "password_hash" not in body

    assert set(body.keys()) == {
        "id",
        "email",
        "email_verified_at",
        "created_at",
        "updated_at",
    }
    assert body["email_verified_at"] is None


    
# How pytest fixtures work
#
# Fixtures are not normal functions—you never call them yourself.
# The @pytest.fixture decorator registers the function with pytest.
#
# When pytest finds a test like:
#     def test_create_url(client):
#
# it matches the parameter name ("client") to the registered fixture,
# executes the fixture, and runs it until `yield`.
#
# The object yielded (e.g., TestClient) is injected into the test as
# the `client` argument. After the test finishes, pytest resumes the
# fixture after `yield` to perform cleanup.
#
# Lifecycle:
#   Setup -> yield object -> Run test -> Cleanup
#
# By default, each test gets a fresh fixture instance, keeping tests
# isolated and preventing shared state.
#
# Conceptually, pytest behaves like:
#
#   fixture = client()
#   obj = next(fixture)      # setup until yield
#   try:
#       test_create_url(obj)
#   finally:
#       next(fixture)        # cleanup after yield
#
# Note: Fixture injection is based on the parameter name (`client`),
# not the type annotation (`TestClient`), which is only for IDE/type
# checking support.

#=================================================================================

# Why use `yield` in a pytest fixture?
#
# Unlike `return`, `yield` pauses the fixture instead of ending it.
#
# Before `yield`:
#   - Perform setup (create DB, TestClient, overrides, etc.).
#
# At `yield`:
#   - Hand the object to pytest.
#   - Pytest injects it into the test and runs the test.
#
# After the test finishes:
#   - Pytest resumes execution immediately after `yield`.
#   - Cleanup code runs (clear overrides, close resources, rollback, etc.).
#
# Lifecycle:
#   Setup -> yield resource -> Test executes -> Cleanup
#
# Conceptually:
#
#   fixture = client()
#   resource = next(fixture)   # setup until yield
#   test(resource)             # run test
#   next(fixture)              # resume after yield -> cleanup
#
# If `return` were used instead of `yield`, the function would end
# immediately and the cleanup code would never execute.