import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.services.auth_service import EmailTakenError, register_user
from app.utils.security import verify_password
from app.utils.snowflake import SnowflakeGenerator

from time import time_ns

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
                user=await register_user(
                    session=session,
                    email=f" {email.upper()} ", #Don't use fixed emails in integration tests.
                    password="a-secure-password",
                    generator=SnowflakeGenerator(worker_id=0),
                )

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
