import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.services.auth_service import (EmailTakenError, register_user, EmailUnverifiedError, 
                                       InvalidCredentialsError,authenticate_user,
                                       AccountLockedError,decode_refresh_token,hash_token_identifier,)
from app.utils.security import verify_password
from app.utils.snowflake import SnowflakeGenerator

from datetime import datetime, timedelta, timezone

from app.models.user import User

from app.utils.security import hash_password

from time import time_ns

from datetime import datetime, timedelta, timezone

from app.repositories.auth_repository import get_refresh_token_by_token_hash
from app.services.auth_service import issue_token_pair

from app.models.email_verification_token import EmailVerificationToken
from app.services.auth_service import verify_email
from app.utils.security import generate_opaque_token

from sqlalchemy import select

def test_register_user_normalizes_email_and_hashes_password() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory=async_sessionmaker(engine,expire_on_commit=False)

        email = f"user-{time_ns()}@example.com"

        try:
            async with session_factory() as session:
                registration=await register_user(
                    session=session,
                    email=f" {email.upper()} ", #Don't use fixed emails in integration tests.
                    password="a-secure-password",
                    generator=SnowflakeGenerator(worker_id=0),
                )
                user=registration.user

                assert user.email==f"{email}"
                assert user.password_hash is not None
                assert verify_password("a-secure-password", user.password_hash)

                await session.rollback()
#The rollback is there to ensure the test doesn't leave data in the database.
#Without it, the test would pollute the database and affect later tests.

        finally:
            await engine.dispose()
    asyncio.run(check())

def test_register_user_rejects_normalized_duplicate_email() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        email = f"user-{time_ns()}@example.com"

        try:
            async with session_factory() as session:
                generator = SnowflakeGenerator(worker_id=0)

                await register_user(
                    session,
                    f" {email.upper()} ",
                    "a-secure-password",
                    generator,
                )
                await session.flush()

                with pytest.raises(EmailTakenError):
                    await register_user(
                        session,
                        f" {email.upper()} ",
                        "another-secure-password",
                        generator,
                    )
# register_user() should detect an existing normalized email and raise
# EmailTakenError before PostgreSQL raises an IntegrityError on flush().

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

def test_authenticate_user_returns_verified_user()->None:
    async def check()->None:
        engine=create_async_engine(get_settings().database_url,
                                   poolclass=NullPool,)
        session_factory=async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with session_factory() as session:
                user=User(
                    id=SnowflakeGenerator(worker_id=0).next_id(),
                    email=f"user-{time_ns()}@example.com",
                    password_hash=hash_password("hello12345678"),
                    email_verified_at=datetime.now(timezone.utc),
                )
                session.add(user)
                await session.flush()
                authenticated = await authenticate_user(
                    session=session,
                    email=user.email.upper(),
                    password="hello12345678",
                )
                assert authenticated.id==user.id 
                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())
# session.add() is synchronous because it only registers the object with
# SQLAlchemy's in-memory session; it does not communicate with the database.
# Database I/O happens later during flush() or commit(), which are async and
# therefore must be awaited.

def test_authenticate_user_rejects_invalid_credentials() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with session_factory() as session:
                user = User(
                    id=SnowflakeGenerator(worker_id=0).next_id(),
                    email=f"user-{time_ns()}@example.com",
                    password_hash=hash_password("hello12345678"),
                    email_verified_at=datetime.now(timezone.utc),
                )
                session.add(user)
                await session.flush()

                with pytest.raises(InvalidCredentialsError):
                    await authenticate_user(
                        session=session,
                        email=user.email,
                        password="wrong-password",
                    )
                    await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

def test_authenticate_user_rejects_unverified_password_account() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with session_factory() as session:
                user = User(
                    id=SnowflakeGenerator(worker_id=0).next_id(),
                    email=f"user-{time_ns()}@example.com",
                    password_hash=hash_password("hello12345678"),
                )
                session.add(user)
                await session.flush()

                with pytest.raises(EmailUnverifiedError):
                    await authenticate_user(
                        session=session,
                        email=user.email,
                        password="hello12345678",
                    )

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

def test_authenticate_user_rejects_currently_locked_account() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with session_factory() as session:
                user = User(
                    id=SnowflakeGenerator(worker_id=0).next_id(),
                    email=f"user-{time_ns()}@example.com",
                    password_hash=hash_password("hello12345678"),
                    email_verified_at=datetime.now(timezone.utc),
                    locked_until=datetime.now(timezone.utc) + timedelta(minutes=15),
                )
                session.add(user)
                await session.flush()

                with pytest.raises(AccountLockedError):
                    await authenticate_user(
                        session=session,
                        email=user.email,
                        password="hello12345678",
                    )

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

def test_authenticate_user_locks_account_after_five_failed_attempts() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with session_factory() as session:
                user = User(
                    id=SnowflakeGenerator(worker_id=0).next_id(),
                    email=f"user-{time_ns()}@example.com",
                    password_hash=hash_password("hello12345678"),
                    email_verified_at=datetime.now(timezone.utc),
                )
                session.add(user)
                await session.flush()

                for _ in range(5):
                    with pytest.raises(InvalidCredentialsError):
                        await authenticate_user(
                            session=session,
                            email=user.email,
                            password="wrong-password",
                        )

                assert user.failed_login_count == 5
                assert user.locked_until is not None
                assert user.locked_until > datetime.now(timezone.utc)

                with pytest.raises(AccountLockedError):
                    await authenticate_user(
                        session=session,
                        email=user.email,
                        password="hello12345678",
                    )

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())
#authenticate_user() currently raises InvalidCredentialsError
# immediately on an incorrect password without updating the User object. As a
# result:
#
#   - failed_login_count is never incremented (remains 0),
#   - locked_until is never set (remains None),
#   - the account is never locked.
#
# The test defines the desired behavior: each failed login should increment
# failed_login_count, the fifth failure should create the lock, and only the
# following login attempt should raise AccountLockedError.

def test_authenticate_user_resets_failure_state_after_successful_login() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with session_factory() as session:
                user = User(
                    id=SnowflakeGenerator(worker_id=0).next_id(),
                    email=f"user-{time_ns()}@example.com",
                    password_hash=hash_password("hello12345678"),
                    email_verified_at=datetime.now(timezone.utc),
                    failed_login_count=3,
                    locked_until=datetime.now(timezone.utc) - timedelta(minutes=1),
                )
                session.add(user)
                await session.flush()

                authenticated = await authenticate_user(
                    session=session,
                    email=user.email,
                    password="hello12345678",
                )

                assert authenticated.id == user.id
                assert user.failed_login_count == 0
                assert user.locked_until is None

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

#The same input always produces the same output.
def test_token_identifier_hash_is_deterministic_and_keyed() -> None:
    token_id="refreshtoken-jti"
    first = hash_token_identifier(
        token_id,
        secret="token-hash-secret",
    )
    second = hash_token_identifier(
        token_id,
        secret="token-hash-secret",
    )
    different_secret = hash_token_identifier(
        token_id,
        secret="different-token-hash-secret",
    )
    assert first == second
    assert first != different_secret
    assert len(first) == 64
    assert token_id not in first
# `jti` (JWT ID) is a unique identifier embedded in the refresh token itself.
# For security, the server does not store this raw identifier. Instead, it
# stores a keyed hash of the `jti`. When a refresh token is presented later,
# the server extracts its `jti`, hashes it again, and looks up the stored hash.
# The hash must therefore be deterministic (same input → same output) and
# keyed (different secrets → different hashes) to allow secure, reliable
# refresh-token validation.
#===============================================================================================================
# Unlike previous tests that checked one function, this one verifies that multiple components work together.
# It tests the complete flow of issuing a token pair.
# Integration test for issuing a token pair. It verifies that issue_token_pair()
# creates valid access and refresh JWTs, hashes the refresh token's `jti`,
# persists the corresponding RefreshToken record, and stores the correct
# user_id, token_hash, and family_id. It ensures the JWT utilities, hashing,
# repository, and service layer all work together correctly.
def test_issue_token_pair_persists_hashed_refresh_identifier() -> None:
    async def check() -> None:
        settings = get_settings()
        engine = create_async_engine(
            settings.database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        generator = SnowflakeGenerator(worker_id=0)

        try:
            async with session_factory() as session:
                user=User(
                    id=generator.next_id(),
                   email=f"user-{time_ns()}@example.com",
                    password_hash=hash_password("hello12345678"),
                    email_verified_at=datetime.now(timezone.utc),
                    auth_version=1,
                )
                session.add(user)
                await session.flush()

                token_pair = await issue_token_pair(
                    session=session,
                    user=user,
                    generator=generator,
                )

                claims = decode_refresh_token(
                    token_pair.refresh_token,
                    secret=settings.jwt_secret,
                    issuer=settings.jwt_issuer,
                    audience=settings.jwt_audience,
                )

                token_hash = hash_token_identifier(
                    str(claims["jti"]),
                    secret=settings.token_hash_secret,
                )

                stored = await get_refresh_token_by_token_hash(
                    session,
                    token_hash,
                )

                assert token_pair.access_token
                assert token_pair.refresh_token
                assert token_pair.expires_in == settings.access_token_ttl_seconds
                assert stored is not None
                assert stored.user_id == user.id
                assert stored.token_hash == token_hash
                assert str(stored.family_id) == claims["family_id"]

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())



# The access token stores an absolute expiration time (`exp`) because JWTs
# must know the exact timestamp after which they become invalid. Separately,
# the API response returns `expires_in` (the configured lifetime in seconds)
# so the client knows how long the access token is valid and when it should
# proactively refresh it. Both represent the same lifetime, but `exp` is for
# server-side validation while `expires_in` is for client-side scheduling.

def test_verify_email_marks_user_and_consumes_token()->None:
    async def check()->None:
        settings=get_settings()
        engine = create_async_engine(
            settings.database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        user_id = time_ns()
        raw_token = generate_opaque_token()

        try:
            async with session_factory() as session:
                user=User( 
                    id=user_id,
                    email=f"user-{user_id}@example.com",
                    password_hash="password-hash",
                )
                token = EmailVerificationToken(
                    id=user_id + 1,
                    user_id=user_id,
                    token_hash=hash_token_identifier(
                        raw_token,
                        secret=settings.token_hash_secret,
                    ),
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
                )

                session.add(user)
                await session.flush()

                session.add(token)
                await session.flush()

                verified_user = await verify_email(
                    session=session,
                    token=raw_token,
                )
                assert verified_user.id == user.id
                assert user.email_verified_at is not None
                assert token.consumed_at is not None

                await session.rollback()
        finally:
            await engine.dispose()


    asyncio.run(check())


def test_register_user_creates_unconsumed_verification_token()->None:
    async def check()->None:
        engine=create_async_engine(get_settings().database_url,poolclass=NullPool)

        session_factory=async_sessionmaker(engine,expire_on_commit=False)

        now=datetime.now(timezone.utc)

        try:
            async with session_factory() as session:
                registration = await register_user(
                    session=session,
                    email=f"user-{time_ns()}@example.com",
                    password="a-secure-password",
                    generator=SnowflakeGenerator(worker_id=0),
                )
                user = registration.user

                result = await session.execute(
                    select(EmailVerificationToken).where(
                        EmailVerificationToken.user_id == user.id
                    )
                )
                token=result.scalar_one()
                
                assert token.token_hash == hash_token_identifier(
                registration.verification_token,
                secret=get_settings().token_hash_secret,
                )       

                assert token.consumed_at is None
                assert token.expires_at > now
                assert len(token.token_hash) == 64

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())