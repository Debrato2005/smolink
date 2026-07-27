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




def test_user_model() -> None:
    table = User.__table__

    assert table.name == "users"
    assert isinstance(table.c.id.type, BigInteger)
    assert table.c.id.primary_key
    assert not table.c.id.autoincrement
    assert table.c.email.unique
    assert table.c.email.index
    assert not table.c.email.nullable
    assert not table.c.password_hash.nullable
    assert "created_at" in table.c
    assert "updated_at" in table.c

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