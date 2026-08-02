import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.services.auth_service import EmailTakenError, register_user
from app.utils.security import verify_password
from app.utils.snowflake import SnowflakeGenerator

def test_register_user_normalizes_email_and_hashes_password() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory=async_sessionmaker(engine,expire_on_commit=False)

        try:
            async with session_factory() as session:
                user=await register_user(
                    session=session,
                    email=" User@Example.COM ",
                    password="a-secure-password",
                    generator=SnowflakeGenerator(worker_id=0),
                )

                assert user.email=="user@example.com"
                assert user.password_hash is not None
                assert verify_password("a-secure-password", user.password_hash)

                await session.rollback()
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

        try:
            async with session_factory() as session:
                generator = SnowflakeGenerator(worker_id=0)

                await register_user(
                    session,
                    "user@example.com",
                    "a-secure-password",
                    generator,
                )
                await session.flush()

                with pytest.raises(EmailTakenError):
                    await register_user(
                        session,
                        " USER@EXAMPLE.COM ",
                        "another-secure-password",
                        generator,
                    )
# register_user() should detect an existing normalized email and raise
# EmailTakenError before PostgreSQL raises an IntegrityError on flush().

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())
