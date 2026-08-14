from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.url import Url
from app.repositories.url_repository import create_url, get_url_by_short_code
from app.utils.aliases import InvalidAliasError, normalize_alias
from app.utils.base62 import encode_base62
from app.utils.snowflake import SnowflakeGenerator


class AliasTakenError(Exception):
    pass
class InvalidExpiryError(Exception):
    pass

async def create_short_url(
    session: AsyncSession,
    destination: str,
    alias: str | None,
    expires_at: datetime | None,
    owner_id: int | None,
    generator: SnowflakeGenerator,
) -> Url:
    
    if expires_at is not None and expires_at <= datetime.now(timezone.utc):
        raise InvalidExpiryError("Expiry must be in the future")

    url_id = generator.next_id()

    if alias is None:
        short_code = encode_base62(url_id)
    else:
        short_code = normalize_alias(alias)

        if await get_url_by_short_code(session, short_code) is not None:
            raise AliasTakenError("Alias is already taken")

    url = Url(
        id=url_id,
        short_code=short_code,
        destination=destination,
        owner_id=owner_id,
        expires_at=expires_at,
    )

    return await create_url(session, url)


