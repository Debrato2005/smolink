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

async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
# Refresh tokens identify the user by the JWT `sub` (user ID) claim rather than
# email. After validating the refresh token, we load the corresponding user by
# ID to verify the account is still valid before issuing a new token pair.