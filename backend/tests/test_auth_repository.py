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
)


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