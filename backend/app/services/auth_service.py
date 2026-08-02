from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import create_user, get_user_by_email
from app.utils.security import hash_password, normalize_email
from app.utils.snowflake import SnowflakeGenerator

class EmailTakenError(Exception):
    pass

async def register_user(
        session:AsyncSession,
        email:str,
        password: str,
        generator: SnowflakeGenerator,
)->User:
    normalized_email=normalize_email(email)

    if await get_user_by_email(session,normalized_email) is not None:
        raise EmailTakenError(("Email is already registered"))

    user=User(
        id=generator.next_id(),
        email=normalized_email,
        password_hash=hash_password(password),
    )
    return await create_user(session,user)