import asyncio
from time import time_ns

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.models.user import User
from app.repositories.user_repository import create_user, get_user_by_email


def test_create_and_find_user_by_email() -> None:
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
                user = User(
                    id=user_id,
                    email=email,
                    password_hash="hashed-password",
                )

                await create_user(session, user)
                await session.flush()

                found = await get_user_by_email(session, email)

                assert found is not None
                assert found.id == user_id
                assert found.email == email

                await session.rollback()
        finally:
            await engine.dispose()

    asyncio.run(check())

# Repository Layer
#
# The repository layer encapsulates all database access logic, providing a
# clean interface for creating, querying, updating, and deleting models while
# hiding SQLAlchemy implementation details from the rest of the application.
#
# Models define *what* the database schema looks like (tables, columns,
# relationships), whereas repositories define *how* data is persisted and
# retrieved. Routes and services interact with repositories instead of writing
# SQLAlchemy queries directly, improving separation of concerns, code reuse,
# maintainability, and testability.
#
# This test verifies that the User repository correctly persists a User model
# and can retrieve it by email, ensuring the repository interacts correctly
# with the database.