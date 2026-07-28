#Repository Layer. It is responsible for all communication with the database.
import asyncio
from time import time_ns
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.core.config import get_settings
from app.models.url import Url
from app.repositories.url_repository import create_url, get_url_by_short_code

def test_url_repository_creates_and_looks_up_url() -> None:
    async def check() -> None:
        engine = create_async_engine(
            get_settings().database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        url_id = time_ns()
        short_code = f"repo-{url_id}"

        try:
            async with session_factory() as session:
                url = Url(
                    id=url_id,
                    short_code=short_code,
                    destination="https://example.com",
                )

                created = await create_url(session, url)
                found = await get_url_by_short_code(session, short_code)

                assert created.id == url_id
                assert found is not None
                assert found.destination == "https://example.com"

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())