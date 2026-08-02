from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    return user


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()