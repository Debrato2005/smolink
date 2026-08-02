from sqlalchemy import BigInteger

from app.models.user import User
from app.models.url import Url
from app.models.click_event import ClickEvent

import asyncio
from time import time_ns
import pytest
from sqlalchemy.exc import IntegrityError
from app.core.config import get_settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.models.url import Url
from app.models.user import User

from app.models.auth_identity import AuthIdentity
from app.models.refresh_token import RefreshToken
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken
from app.models.oauth_authorization_request import OAuthAuthorizationRequest

def test_user_model() -> None:
    table = User.__table__

    assert table.name == "users"
    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert not table.c.id.autoincrement
    assert table.c.email.unique
    assert table.c.email.index
    assert not table.c.email.nullable
    assert "created_at" in table.c
    assert "updated_at" in table.c
    assert table.c.password_hash.nullable
    assert "email_verified_at" in table.c
    assert table.c.email_verified_at.nullable
    assert "failed_login_count" in table.c
    assert not table.c.failed_login_count.nullable
    assert table.c.failed_login_count.server_default is not None
    assert "locked_until" in table.c
    assert table.c.locked_until.nullable
    assert "auth_version" in table.c
    assert not table.c.auth_version.nullable
    assert table.c.auth_version.server_default is not None

def test_url_model() -> None:
    table = Url.__table__

    assert table.name == "urls"
    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert not table.c.id.autoincrement
    assert table.c.short_code.unique
    assert table.c.short_code.index
    assert not table.c.short_code.nullable
    assert not table.c.destination.nullable
    assert table.c.owner_id.nullable
    assert next(iter(table.c.owner_id.foreign_keys)).ondelete == "SET NULL"
    assert table.c.total_clicks.server_default is not None
    assert "expires_at" in table.c
    assert "last_clicked_at" in table.c
    assert "created_at" in table.c
    assert "updated_at" in table.c

def test_click_event_model_has_required_columns() -> None:
    table = ClickEvent.__table__

    assert table.name == "click_events"
    assert isinstance(table.c.id.type, BigInteger)
    assert not table.c.id.autoincrement
    assert not table.c.url_id.nullable
    assert next(iter(table.c.url_id.foreign_keys)).ondelete == "CASCADE"
    assert not table.c.ip_hash.nullable
    assert "clicked_at" in table.c
    assert "browser" in table.c
    assert "os" in table.c
    assert "device" in table.c
    assert "referrer" in table.c
    assert any(
        list(index.columns.keys()) == ["url_id", "clicked_at"]
        for index in table.indexes
    )

# NOTE:
# These tests intentionally create a fresh AsyncEngine with NullPool instead of
# reusing the application's global engine. Each test is executed via
# `asyncio.run()`, which creates a new event loop. asyncpg connections are bound
# to the event loop that created them, so reusing pooled connections across
# different test event loops raises:
#
#     RuntimeError: Future attached to a different loop
#
# Using a per-test engine with NullPool guarantees that every test gets fresh
# connections tied to its own event loop. In the actual FastAPI application,
# the global engine and connection pool are reused because the server runs on a
# long-lived event loop.

def test_database_enforces_unique_email() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        user_id = time_ns()
        email = f"user-{user_id}@example.com"

        try:
            async with session_factory() as session:
                session.add_all(
                    [
                        User(id=user_id, email=email, password_hash="hash-one"),
                        User(
                            id=user_id + 1,
                            email=email,
                            password_hash="hash-two",
                        ),
                    ]
                )

                with pytest.raises(IntegrityError):
                    await session.flush()

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())


def test_database_enforces_url_owner_foreign_key() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        url_id = time_ns()

        try:
            async with session_factory() as session:
                session.add(
                    Url(
                        id=url_id,
                        short_code=f"missing-owner-{url_id}",
                        destination="https://example.com",
                        owner_id=url_id + 1,
                    )
                )

                with pytest.raises(IntegrityError):
                    await session.flush()

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

# Authentication-related tables each represent a distinct security concept with
# its own lifecycle. AuthIdentity maps users to login providers (password,
# Google, GitHub, etc.). RefreshToken enables secure session management,
# rotation, revocation, and logout. EmailVerificationToken and
# PasswordResetToken store one-time, expiring tokens for account verification
# and password recovery. OAuthAuthorizationRequest persists temporary OAuth
# state (state, nonce, PKCE verifier) to securely complete the authorization
# flow and prevent CSRF and replay attacks.

def test_auth_identity_model() -> None:
    table = AuthIdentity.__table__

    assert table.name == "auth_identities"
    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert not table.c.id.autoincrement
    assert not table.c.user_id.nullable
    assert next(iter(table.c.user_id.foreign_keys)).ondelete == "CASCADE"
    assert not table.c.provider.nullable
    assert not table.c.provider_subject.nullable
    assert any(
        list(constraint.columns.keys()) == ["provider", "provider_subject"]
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    )
# AuthIdentity separates a user's identity from their authentication methods.
# A User represents the person, while AuthIdentity records how that user logs
# in (password, Google, GitHub, Apple, etc.). This allows one user to have
# multiple login providers without adding provider-specific columns to the
# users table, keeping the schema normalized and easily extensible.

def test_refresh_token_model() -> None:
    table = RefreshToken.__table__

    assert table.name == "refresh_tokens"
    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert not table.c.id.autoincrement

    assert not table.c.user_id.nullable
    assert next(iter(table.c.user_id.foreign_keys)).ondelete == "CASCADE"
    assert table.c.user_id.index

    assert not table.c.token_hash.nullable
    assert table.c.token_hash.unique
    assert not table.c.family_id.nullable
    assert table.c.family_id.index

    assert "parent_token_id" in table.c
    assert table.c.parent_token_id.nullable
    assert "issued_at" in table.c
    assert "expires_at" in table.c
    assert "used_at" in table.c
    assert "revoked_at" in table.c

# Why keep a refresh token table?
#
# Refresh tokens are stateful, unlike short-lived stateless access tokens.
# The server must remember every issued refresh token (typically as a hash)
# so it can verify that the token is still active and has not been revoked,
# rotated, expired, or reused. Without a refresh token table, secure logout,
# per-device session management, refresh-token rotation with reuse detection,
# and forced session invalidation after password changes or security incidents
# would not be possible.

def test_email_verification_token_model() -> None:
    table = EmailVerificationToken.__table__

    assert table.name == "email_verification_tokens"
    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert not table.c.id.autoincrement

    assert not table.c.user_id.nullable
    assert next(iter(table.c.user_id.foreign_keys)).ondelete == "CASCADE"
    assert table.c.user_id.index

    assert not table.c.token_hash.nullable
    assert table.c.token_hash.unique
    assert "expires_at" in table.c
    assert not table.c.expires_at.nullable
    assert "consumed_at" in table.c
    assert table.c.consumed_at.nullable

def test_password_reset_token_model() -> None:
    table = PasswordResetToken.__table__

    assert table.name == "password_reset_tokens"
    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert not table.c.id.autoincrement

    assert not table.c.user_id.nullable
    assert next(iter(table.c.user_id.foreign_keys)).ondelete == "CASCADE"
    assert table.c.user_id.index

    assert not table.c.token_hash.nullable
    assert table.c.token_hash.unique
    assert not table.c.expires_at.nullable
    assert table.c.consumed_at.nullable

def test_oauth_authorization_request_model() -> None:
    table = OAuthAuthorizationRequest.__table__

    assert table.name == "oauth_authorization_requests"
    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert not table.c.id.autoincrement

    assert not table.c.state_hash.nullable
    assert table.c.state_hash.unique
    assert not table.c.nonce.nullable
    assert not table.c.pkce_verifier.nullable
    assert not table.c.expires_at.nullable
    assert table.c.consumed_at.nullable

def test_database_enforceS_unique_provider_subject()->None:
    async def check()->None:
        engine=create_async_engine(get_settings().database_url,poolclass=NullPool,)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        user_id = time_ns()

        try:
            async with session_factory() as session:
                session.add(
                    User(
                        id=user_id,
                        email=f"user-{user_id}@example.com",
                        password_hash=None,
                    )
                )
                await session.flush()
                session.add_all(
                    [
                        AuthIdentity(
                            id=user_id + 1,
                            user_id=user_id,
                            provider="google",
                            provider_subject="google-subject",
                        ),
                        AuthIdentity(
                            id=user_id + 2,
                            user_id=user_id,
                            provider="google",
                            provider_subject="google-subject",
                        ),
                    ]
                )
                with pytest.raises(IntegrityError):
                    await session.flush()

                await session.rollback()
        finally :
            await engine.dispose()

    asyncio.run(check())



# Authentication is composed of multiple specialized models and token types,
# each representing a different security artifact with its own purpose,
# lifecycle, expiration policy, and validation rules.
#
# Persistent models:
# - User: Permanent account and profile information.
# - AuthIdentity: Maps a user to one or more authentication providers
#   (password, Google, GitHub, Apple, etc.), allowing multiple login methods
#   without provider-specific columns in the users table.
#
# Temporary security artifacts:
# - EmailVerificationToken: One-time token proving ownership of an email.
# - PasswordResetToken: One-time token authorizing a password reset.
# - OAuthAuthorizationRequest: Temporary OAuth/OpenID Connect state (state,
#   nonce, PKCE verifier) used to securely complete external login flows.
# - RefreshToken: Long-lived, stateful session token stored as a hash to
#   support logout, token rotation, revocation, per-device sessions, and
#   replay/reuse detection.
#
# JWT Access Tokens are intentionally NOT stored in the database. They are
# short-lived, stateless, self-contained tokens containing signed user claims
# that can be verified using the server's signing key without a database
# lookup. Refresh tokens, however, must be persisted because the server needs
# to track whether they are active, expired, revoked, rotated, or already used.
#
# Typical authentication lifecycle:
# Register
#   -> User + EmailVerificationToken
# Verify Email
#   -> EmailVerificationToken consumed
# Login
#   -> JWT Access Token + RefreshToken issued
# Access Token Expires
#   -> RefreshToken exchanged for a new JWT and a rotated RefreshToken
# Logout
#   -> RefreshToken revoked
# Forgot Password
#   -> PasswordResetToken generated and later consumed
# OAuth Login
#   -> OAuthAuthorizationRequest created, validated, then consumed
#
# The system intentionally generates different tokens for different tasks
# rather than reusing a single token everywhere. Each token has exactly one
# responsibility, follows the principle of least privilege, and can be
# independently expired, revoked, rotated, or consumed, resulting in a more
# secure, maintainable, and extensible authentication architecture.