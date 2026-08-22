import asyncio
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

from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta, timezone

from uuid import uuid4

from app.models.user import User

from app.models.email_verification_token import EmailVerificationToken
from app.utils.security import (
    generate_opaque_token,
    hash_password,
    hash_token_identifier,
    create_refresh_token,
)

from app.models.password_reset_token import PasswordResetToken

# Automatically replace the real email sender for every route test. This keeps
# tests deterministic and isolated by preventing outbound HTTP requests to
# Resend while still allowing the application code to execute its normal email
# dispatch path. Individual tests can override this patch to inspect the email
# arguments or exercise different behaviors.
@pytest.fixture(autouse=True)
def suppress_verification_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_send_verification_email(
        *,
        recipient_email: str,
        verification_token: str,
        idempotency_key: str,
    ) -> None:
        return None

    monkeypatch.setattr(
        "app.api.v1.endpoints.auth.send_verification_email",
        fake_send_verification_email,
    )
    async def fake_send_password_reset_email(
        *,
        recipient_email: str,
        reset_token: str,
        idempotency_key: str,
    ) -> None:
        return None

    monkeypatch.setattr(
        "app.api.v1.endpoints.auth.send_password_reset_email",
        fake_send_password_reset_email,
    )

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

    async def clear_auth_rate_limit() -> None:
        redis_client = Redis.from_url(get_settings().redis_url)
        try:
            await redis_client.delete("rate:auth:testclient")
        finally:
            await redis_client.aclose()
#dependency_overrides is a dictionary.
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_redis_client] = override_get_redis_client

    asyncio.run(clear_auth_rate_limit()) #Every auth API test will now start and end with a clean rate-limit key
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        asyncio.run(clear_auth_rate_limit())
        app.dependency_overrides.clear()
# Clear the shared auth rate-limit Redis key before and after every auth API
# test. Register and login intentionally use the same limiter key
# (`rate:auth:testclient`), so without cleanup one test's requests would carry
# over into later tests, causing nondeterministic 429 responses. The dedicated
# rate-limit test still verifies the limiter itself by exhausting the limit
# within a single test.


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

def test_register_rejects_duplicate_normalized_email(client: TestClient) -> None:
    email = f"agent-{time_ns()}@example.com"

    first = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "hello12345678"},
    )
    second = client.post(
        "/api/v1/auth/register",
        json={"email": f"  {email.upper()}  ", "password": "hello12345678"},
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json() == {
        "error": "email_taken",
        "message": "Email is already registered",
    }

def test_register_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "too-short"},
    )

    assert response.status_code == 422

def test_register_returns_429_after_five_requests(client: TestClient) -> None:
    key = "rate:auth:testclient"

    async def clear_limit() -> None:
        redis_client = Redis.from_url(get_settings().redis_url)
        try:
            await redis_client.delete(key)
        finally:
            await redis_client.aclose()

    asyncio.run(clear_limit())

    try:
        for _ in range(5):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"agent-{time_ns()}@example.com",
                    "password": "hello12345678",
                },
            )
            assert response.status_code == 201

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"agent-{time_ns()}@example.com",
                "password": "hello12345678",
            },
        )

        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) > 0
    finally:
        asyncio.run(clear_limit())

def test_register_maps_database_unique_race_to_409(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def concurrent_duplicate(*args: object, **kwargs: object) -> None:
        raise IntegrityError("INSERT", {}, Exception("duplicate key"))

    monkeypatch.setattr(
        "app.api.v1.endpoints.auth.register_user",
        concurrent_duplicate,
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"agent-{time_ns()}@example.com",
            "password": "hello12345678",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": "email_taken",
        "message": "Email is already registered",
    }



    
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

#=================================================================================================

# Why have both tests/test_auth.py and tests/test_auth_service.py?
#
# They test different layers of the authentication system.
#
# tests/test_auth_service.py
# --------------------------
# Unit tests for the AuthService business logic in isolation. Dependencies
# (database, Redis, email sender, JWT service, etc.) are typically mocked or
# stubbed. These tests verify authentication logic such as:
#   - Email normalization
#   - Password hashing and verification
#   - Duplicate email detection
#   - Account lockout logic
#   - Token generation
#   - Domain exceptions raised by the service
#
# tests/test_auth.py
# ------------------
# Integration/API tests for the authentication endpoints. These send real HTTP
# requests through FastAPI and verify the complete request lifecycle:
#
#   HTTP Request
#       ↓
#   FastAPI routing
#       ↓
#   Pydantic request validation
#       ↓
#   Dependency injection (DB, Redis, rate limiter, etc.)
#       ↓
#   AuthService
#       ↓
#   Exception handlers
#       ↓
#   HTTP Response
#
# These tests verify:
#   - API contract (status codes, JSON responses, headers)
#   - Request validation (422)
#   - Rate limiting (429)
#   - Authentication dependencies
#   - Correct mapping of service/database errors to HTTP responses
#     (e.g. IntegrityError → 409 Conflict)
#
# Passing service tests does not guarantee the HTTP API behaves correctly, and
# passing endpoint tests does not guarantee every business rule is independently
# validated. Both layers are required for comprehensive production-grade testing.




# `*` makes all following parameters keyword-only. This forces callers to write
# `locked_until=...`, making test setup more explicit and preventing accidental
# positional arguments.
def create_verified_user(
    *,
    locked_until: datetime | None = None,)->tuple[int,str]:
    async def seed()->tuple[int,str]:
        engine=create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory=async_sessionmaker(engine,expire_on_commit=False)
        user_id=time_ns()
        email = f"user-{user_id}@example.com"

        try:
            async with session_factory() as session:
                session.add(
                    User(
                        id=user_id,
                        email=email,
                        password_hash=hash_password("hello12345678"),
                        email_verified_at=datetime.now(timezone.utc),
                        locked_until=locked_until, 
                    )
                )
                await session.commit()
        finally:
            await engine.dispose()

        return user_id, email

    return asyncio.run(seed())
# Helper used by login endpoint tests to seed the database with a real,
# email-verified user. It creates and commits the user in its own async
# database session so the login endpoint, which runs in a separate session,
# can query and authenticate it. Unique IDs/emails avoid constraint
# collisions across test runs. The helper returns the generated user ID and
# email, and `asyncio.run()` bridges the async seeding logic into a normal
# synchronous pytest test.


def test_login_returns_token_pair_for_verified_user(
    client: TestClient,
) -> None:
    _, email = create_verified_user()

    response=client.post("/api/v1/auth/login",
        json={
            "email": email,
            "password": "hello12345678",
        },
    )
    assert response.status_code==200
    assert response.json()=={
        "access_token": response.json()["access_token"],
        "refresh_token": response.json()["refresh_token"],
        "token_type": "bearer",
        "expires_in": 900,
    }

def test_login_returns_generic_401_for_wrong_password(
    client:TestClient,
)->None:
    _,email=create_verified_user() #seed function

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_credentials",
        "message": "Invalid email or password",
    }

def test_login_rejects_unverified_password_account(client:TestClient)->None:
    email=f"user-{time_ns()}@example.com"

    assert client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "hello12345678"},
    ).status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "hello12345678"},
    )

    assert response.status_code==403
    assert response.json() == {
        "error": "email_unverified",
        "message": "Email verification is required before login",
    }

def test_login_returns_503_when_limiter_is_unavailable(client:TestClient,
monkeypatch:pytest.MonkeyPatch)->None:

    async def unavailable(*args:object,**kwargs:object)->None:
        raise OSError("Redis unavailable")
# Accept any positional and keyword arguments so this test override remains
# compatible with the original dependency's signature, even if FastAPI or the
# application starts passing arguments in the future. The arguments are ignored.
    monkeypatch.setattr(
        "app.api.v1.dependencies.rate_limit.SlidingWindowRateLimiter.check",
        unavailable,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "hello12345678",
        },
    )

    assert response.status_code == 503

def test_login_returns_423_for_locked_accoount(client:TestClient)->None:
    _,email=create_verified_user(locked_until=datetime.now(timezone.utc)+timedelta(minutes=15))

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "hello12345678"},
    )

    assert response.status_code == 423
    assert response.json() == {
        "error": "account_locked",
        "message": "Account is temporarily locked",
    }

def test_login_returns_429_after_five_requests(client: TestClient) -> None:
    payload = {
        "email": "missing@example.com",
        "password": "hello12345678",
    }

    for _ in range(5):
        assert client.post("/api/v1/auth/login", json=payload).status_code == 401

    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0

#tests after refresh tokens rotation feature

def test_refresh_rotates_token_pair(client:TestClient)->None:
    _,email=create_verified_user()
    login=client.post("/api/v1/auth/login",
        json={"email": email, "password": "hello12345678"},
    )
    original_refresh_token = login.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )

    assert response.status_code == 200
    assert response.json()["refresh_token"] != original_refresh_token
    assert response.json()["access_token"]

def test_refresh_token_reuse_revokes_its_family(client: TestClient) -> None:
    _, email = create_verified_user()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "hello12345678"}, 
    ) # to know json requirement see the payload class variables etc
    original_refresh_token = login.json()["refresh_token"]

    rotated = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )
    replacement_refresh_token = rotated.json()["refresh_token"]

    replay = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )
    assert replay.status_code == 401
    assert replay.json()["error"] == "invalid_refresh_token"

    revoked_successor = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": replacement_refresh_token},
    )
    assert revoked_successor.status_code == 401
    assert revoked_successor.json()["error"] == "invalid_refresh_token"
# Verify refresh-token rotation and replay protection.
#
# Flow:
#   1. Log in to obtain the initial refresh token (A).
#   2. Refresh using A, which rotates it into a replacement refresh token (B).
#   3. Replay A. Since A was already consumed, the server detects a replay
#      attack, revokes the entire refresh-token family, and returns 401.
#   4. Verify that B (the latest valid successor) is also rejected because the
#      family revocation invalidates every refresh token from that login session.

def test_refresh_rejects_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not-a-valid-jwt"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_refresh_token",
        "message": "Invalid refresh token",
    }

def test_refresh_rejects_expired_token(client: TestClient) -> None:
    settings = get_settings()
    expired_token = create_refresh_token(
        user_id=1,
        family_id=uuid4(),
        secret=settings.jwt_secret,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        expires_in=timedelta(seconds=-1),
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": expired_token},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_refresh_token"

def test_refresh_rejects_token_without_a_persisted_record(
    client: TestClient,
) -> None:
    settings = get_settings()
    token = create_refresh_token(
        user_id=1,
        family_id=uuid4(),
        secret=settings.jwt_secret,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        expires_in=timedelta(days=30),
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_refresh_token"

def test_verify_email_rejects_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"token": "unknown-token"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": "invalid_or_expired_token",
        "message": "Invalid or expired token",
    }

#helper
def create_pending_verification(
    *,
    expires_at: datetime | None = None,
) -> tuple[int, str]:
    async def seed()->tuple[int,str]:
        settings=get_settings()
        engine=create_async_engine(settings.database_url,poolclass=NullPool)
        session_factory=async_sessionmaker(engine,expire_on_commit=False)

        user_id=time_ns()
        raw_token=generate_opaque_token()

        try:
            async with session_factory() as session:
                user=User(
                    id=user_id,
                    email=f"user-{user_id}@example.com",
                    password_hash=hash_password("hello12345678"),
                )
                session.add(user)
                await session.flush()

                session.add(
                    EmailVerificationToken(
                        id=user_id + 1,
                        user_id=user_id,
                        token_hash=hash_token_identifier(
                            raw_token,
                            secret=settings.token_hash_secret,
                        ),
                        expires_at=expires_at or (datetime.now(timezone.utc) + timedelta(hours=24)),
                    )
              )
                await session.commit()
# commit() automatically performs a flush first, writing all pending SQL
# statements to the database before permanently committing the transaction.              
        finally:
            await engine.dispose()

        return user_id, raw_token

    return asyncio.run(seed())

def test_verify_email_marks_user_verified(client: TestClient) -> None:
    _, raw_token = create_pending_verification()

    response = client.post(
        "/api/v1/auth/verify-email",
        json={"token": raw_token},
    )
    assert response.status_code == 200
    assert response.json()["email_verified_at"] is not None


def test_verify_email_rejects_reused_token(client: TestClient) -> None:
    _, raw_token = create_pending_verification()

    first = client.post(
        "/api/v1/auth/verify-email",
        json={"token": raw_token},
    )
    second = client.post(
        "/api/v1/auth/verify-email",
        json={"token": raw_token},
    )

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["error"] == "invalid_or_expired_token"

def test_verify_email_rejects_expired_token(client:TestClient)->None:
    _,rawtoken=create_pending_verification(
        expires_at=datetime.now(timezone.utc)-timedelta(seconds=1),
    )
    response=client.post("/api/v1/auth/verify-email",
                         json={"token":rawtoken},
                         )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_or_expired_token"

def test_register_dispatches_verification_email(
        client:TestClient,
        monkeypatch:pytest.MonkeyPatch,)->None:
        sent: dict[str,str]={}

        async def fake_verification_mail_sent(
                *,
                recipient_email: str,
                verification_token: str,
                idempotency_key: str,) -> None:
            sent["recipient_email"] = recipient_email
            sent["verification_token"] = verification_token
            sent["idempotency_key"] = idempotency_key
# Idempotency key uniquely identifies this verification email request.
# If the email send is retried (e.g. due to a timeout or transient failure),
# the provider treats repeated requests with the same key as a single operation,
# preventing duplicate verification emails from being delivered.

        monkeypatch.setattr(
            "app.api.v1.endpoints.auth.send_verification_email",
            fake_verification_mail_sent)
        email = f"user-{time_ns()}@example.com"
        response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "hello12345678"},
    )

        assert response.status_code == 201
        assert sent["recipient_email"] == email
        assert sent["verification_token"]
        assert sent["idempotency_key"] == f"verification:{response.json()['id']}"

def test_logout_revokes_refresh_token_family(client:TestClient)->None:
    _,email=create_verified_user() #helper function
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "hello12345678"},
    )
    refresh_token = login.json()["refresh_token"]

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )#When logout revokes the family, the server marks that family as revoked.

    assert logout.status_code == 204
    assert logout.content == b"" #empty response body

    refresh = client.post(#trying to use the same refresh token after logout.
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh.status_code == 401

def test_me_returns_current_verified_user(client:TestClient)->None:
    _,email=create_verified_user() #helper

    login=client.post(
        "api/v1/auth/login",
        json={"email": email, "password": "hello12345678"},
    )
    access_token=login.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code==200
    assert response.json()["email"]==email
    assert "password_hash" not in response.json()

def test_me_requires_access_token(client:TestClient)->None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_forgot_password_always_returns_202(client:TestClient)->None:
    _,known_email=create_verified_user()

    known = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": known_email},
    )

    unknown = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "missing@example.com"},
    )

    assert known.status_code == 202
    assert unknown.status_code == 202
# b"" represents an empty bytes object, meaning the HTTP response has no body.
    assert known.content == b""
    assert unknown.content == b""
# Always return the same 202 response for known and unknown emails so the
# endpoint does not reveal whether an account exists (prevents account
# enumeration). Registration should be handled separately by the frontend.

# Prevent account enumeration: return the same generic response whether an
# email/account exists or not, so attackers cannot use the endpoint as an
# oracle to discover valid registered users for phishing or credential attacks.

def create_pending_password_reset() -> tuple[str, str]:
    async def seed() -> tuple[str, str]:
        settings = get_settings()
        engine = create_async_engine(
            settings.database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )
        user_id = time_ns()
        email = f"user-{user_id}@example.com"
        raw_token = generate_opaque_token()

        try:
            async with session_factory() as session:
                session.add(
                    User(
                        id=user_id,
                        email=email,
                        password_hash=hash_password("old-password-123"),
                        email_verified_at=datetime.now(timezone.utc),
                    )
                )
                
                await session.flush() 

                session.add(
                    PasswordResetToken(
                        id=user_id + 1,
                        user_id=user_id,
                        token_hash=hash_token_identifier(
                            raw_token,
                            secret=settings.token_hash_secret,
                        ),
                        expires_at=datetime.now(timezone.utc)
                        + timedelta(hours=1),
                    )
                )
                await session.commit()
        finally:
            await engine.dispose()

        return email, raw_token

    return asyncio.run(seed())

def test_reset_password_changes_password_and_revokes_sessions(
        client:TestClient,
)->None:
    email,raw_token=create_pending_password_reset()

    response=client.post(
        "/api/v1/auth/reset-password",
        json={
            "token":raw_token,
            "new_password":"new_password123",
        },
    )
    assert response.status_code==204

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "new_password123"},
    )
    assert login.status_code == 200

