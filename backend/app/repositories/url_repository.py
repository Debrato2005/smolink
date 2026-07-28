from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.url import Url


async def create_url(session: AsyncSession, url: Url) -> Url:
    session.add(url)
    await session.flush()
    return url


async def get_url_by_short_code( session: AsyncSession, short_code: str,) -> Url | None:
    result = await session.execute(
        select(Url).where(Url.short_code == short_code)
    )
    
    return result.scalar_one_or_none()