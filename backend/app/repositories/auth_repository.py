from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken

async def create_refresh_token_record(
    session: AsyncSession,
    token: RefreshToken,
) -> RefreshToken:
    session.add(token)
    await session.flush()
    return token


async def get_refresh_token_by_token_hash(
    session: AsyncSession,
    token_hash: str,
) -> RefreshToken | None:
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    return result.scalar_one_or_none()