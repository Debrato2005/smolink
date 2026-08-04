from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.auth_repository import create_refresh_token_record
from app.repositories.user_repository import create_user, get_user_by_email
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token_identifier,
    normalize_email,
    verify_password,
)
from app.utils.snowflake import SnowflakeGenerator

class EmailTakenError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class EmailUnverifiedError(Exception):
    pass

class AccountLockedError(Exception):
    pass

MAX_FAILED_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCK_DURATION = timedelta(minutes=15)

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
async def authenticate_user(
        *,
        session:AsyncSession,
        email:str,
        password:str
)->User:
    user=await get_user_by_email(session,normalize_email(email))

    if user is None or user.password_hash is None:
        raise InvalidCredentialsError

    if (
        user.locked_until is not None and user.locked_until>datetime.now(timezone.utc)
    ):
        raise AccountLockedError

    if not verify_password(password, user.password_hash):
        user.failed_login_count+=1
        if user.failed_login_count>=MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until=datetime.now(timezone.utc)+ ACCOUNT_LOCK_DURATION
        raise InvalidCredentialsError

    user.failed_login_count = 0
    user.locked_until = None

    if user.email_verified_at is None:
        raise EmailUnverifiedError

    return user
#these functions are service-layer functions.
# Their job is to return the authenticated or newly created domain object (User)
#  so the caller can decide what to do next.

@dataclass
class IssuedTokenPair:
    access_token:str
    refresh_token:str
    expires_in:int

async def issue_token_pair(
    *,
    session: AsyncSession,
    user: User,
    generator: SnowflakeGenerator,
) -> IssuedTokenPair:
    settings = get_settings()
    family_id = uuid4()

    access_token = create_access_token(
        user_id=user.id,
        auth_version=user.auth_version,
        secret=settings.jwt_secret,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        expires_in=timedelta(seconds=settings.access_token_ttl_seconds),
    )

    refresh_token = create_refresh_token(
        user_id=user.id,
        family_id=family_id,
        secret=settings.jwt_secret,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        expires_in=timedelta(seconds=settings.refresh_token_ttl_seconds),
    )

    refresh_claims = decode_refresh_token(
        refresh_token,
        secret=settings.jwt_secret,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )

    refresh_record = RefreshToken( #code that creates the database record for the refresh token after generating the JWT.
        id=generator.next_id(),
        user_id=user.id,
        token_hash=hash_token_identifier(
            str(refresh_claims["jti"]),
            secret=settings.token_hash_secret,
        ),
        family_id=family_id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(seconds=settings.refresh_token_ttl_seconds),
    )
    await create_refresh_token_record(session, refresh_record)

    return IssuedTokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_ttl_seconds,
    )
