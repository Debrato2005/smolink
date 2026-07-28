import asyncio
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.core.config import get_settings
from app.services.url_service import create_short_url
from app.utils.snowflake import SnowflakeGenerator
from app.services.url_service import AliasTakenError

def test_create_short_url_generates_guest_code() -> None:
    async def check()->None:
        engine=create_async_engine(get_settings().database_url,poolclass=NullPool,
                                   )
        session_factory=async_sessionmaker(engine,expire_on_commit=False)
        try:
            async with session_factory() as session:
                url=await create_short_url(
                    session=session,
                    destination="https://example.com",
                    alias=None,
                    expires_at=None,
                    owner_id=None,
                    generator=SnowflakeGenerator(worker_id=0),
                )

                assert url.owner_id is None
                assert url.short_code #The short_code should exist and should not be empty.
                assert url.short_code != str(url.id)

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

def test_create_short_url_rejects_past_expiry() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        try:
            async with session_factory() as session:
                with pytest.raises(ValueError, match="future"):  #Why no assert? Because pytest.raises() is itself the assertion.
                    await create_short_url(
                        session=session,
                        destination="https://example.com",
                        alias=None,
                        expires_at=datetime.now(timezone.utc)
                        - timedelta(seconds=1),
                        owner_id=None,
                        generator=SnowflakeGenerator(worker_id=0),
                    )
        finally:
            await engine.dispose()

    asyncio.run(check())

def test_create_short_url_normalizes_and_protects_aliases() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        generator = SnowflakeGenerator(worker_id=0)

        try:
            async with session_factory() as session:
                created = await create_short_url(
                    session=session,
                    destination="https://example.com",
                    alias="My-Link",
                    expires_at=None,
                    owner_id=None,
                    generator=generator,
                )

                assert created.short_code == "my-link"

                with pytest.raises(AliasTakenError):
                    await create_short_url(
                        session=session,
                        destination="https://example.org",
                        alias="my-link",
                        expires_at=None,
                        owner_id=None,
                        generator=generator,
                    )

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())