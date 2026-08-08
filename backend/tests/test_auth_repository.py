import asyncio
from datetime import datetime, timedelta, timezone
from time import time_ns
from uuid import uuid4

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.auth_repository import (
    create_refresh_token_record,
    get_refresh_token_by_token_hash,
    revoke_refresh_token_family,
     create_email_verification_token,
    get_email_verification_token_by_hash_for_update,
)
from app.models.email_verification_token import EmailVerificationToken


def test_refresh_token_repository_creates_and_looks_up_record() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        user_id = time_ns()
        token_hash = f"token-hash-{user_id}"

        try:
            async with session_factory() as session:
                session.add(
                    User(
                        id=user_id,
                        email=f"user-{user_id}@example.com",
                        password_hash="password-hash",
                    )
                )
                await session.flush()

                token = RefreshToken(
                    id=user_id + 1,
                    user_id=user_id,
                    token_hash=token_hash,
                    family_id=uuid4(),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                )

                created = await create_refresh_token_record(session, token)
                found = await get_refresh_token_by_token_hash(session, token_hash)

                assert created.id == token.id
                assert found is not None
                assert found.user_id == user_id
                assert found.token_hash == token_hash

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

def test_revoke_refresh_token_family_revokes_only_that_family() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        user_id = time_ns()
        family_id = uuid4()
        other_family_id = uuid4()
        now = datetime.now(timezone.utc)

        try:
            async with session_factory() as session:
                session.add(
                    User(
                        id=user_id,
                        email=f"user-{user_id}@example.com",
                        password_hash="password-hash",
                    )
                )
                await session.flush()

                first = RefreshToken(
                    id=user_id + 1,
                    user_id=user_id,
                    token_hash=f"first-{user_id}",
                    family_id=family_id,
                    expires_at=now + timedelta(days=30),
                )
                second = RefreshToken(
                    id=user_id + 2,
                    user_id=user_id,
                    token_hash=f"second-{user_id}",
                    family_id=family_id,
                    expires_at=now + timedelta(days=30),
                )
                unrelated = RefreshToken(
                    id=user_id + 3,
                    user_id=user_id,
                    token_hash=f"other-{user_id}",
                    family_id=other_family_id,
                    expires_at=now + timedelta(days=30),
                )
                session.add_all([first, second, unrelated])
                await session.flush()

                await revoke_refresh_token_family(session, family_id, now)
                await session.flush()
                await session.refresh(first)
                await session.refresh(second)
                await session.refresh(unrelated)

                assert first.revoked_at == now
                assert second.revoked_at == now
                assert unrelated.revoked_at is None

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())
# Ensure revoke_refresh_token_family() only revokes refresh tokens belonging
# to the target family by marking their revoked_at timestamp, without
# affecting unrelated refresh-token families.

def test_email_verification_token_repository_creates_and_locks_record()->None:
    async def check()->None:
        engine=create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        user_id = time_ns()
        token_hash = f"verification-hash-{user_id}"
        try:
            async with session_factory() as session:
                session.add(
                    User(
                        id=user_id,
                        email=f"user-{user_id}@example.com",
                        password_hash="password-hash",
                    )
                )
                await session.flush()
                
                token = EmailVerificationToken(
                    id=user_id + 1,
                    user_id=user_id,
                    token_hash=token_hash,
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
                )
                await create_email_verification_token(session, token)
                found = await get_email_verification_token_by_hash_for_update(
                    session,
                    token_hash,
                )

                assert found is not None
                assert found.id == token.id
                assert found.user_id == user_id

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())