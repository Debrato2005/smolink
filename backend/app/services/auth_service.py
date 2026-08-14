from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4,UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.refresh_token import RefreshToken
from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.repositories.auth_repository import (
    create_refresh_token_record,
    get_refresh_token_by_token_hash_for_update,
    revoke_refresh_token_family,
    get_email_verification_token_by_hash_for_update,
    create_email_verification_token,
    create_password_reset_token,
)
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_id,
)
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token_identifier,
    normalize_email,
    verify_password,
    InvalidRefreshJwtError,
    generate_opaque_token,
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

class InvalidRefreshTokenError(Exception):
    pass

MAX_FAILED_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCK_DURATION = timedelta(minutes=15)

VERIFICATION_TOKEN_TTL=timedelta(hours=24)

@dataclass
class RegistrationResult:
    user:User
    verification_token:str


async def register_user(
        session:AsyncSession,
        email:str,
        password: str,
        generator: SnowflakeGenerator,
)->RegistrationResult:
    normalized_email=normalize_email(email)

    if await get_user_by_email(session,normalized_email) is not None:
        raise EmailTakenError(("Email is already registered"))

    user=User(
        id=generator.next_id(),
        email=normalized_email,
        password_hash=hash_password(password),
    )
    await create_user(session,user)
    await session.flush()

    raw_token=generate_opaque_token()
    verification_token=EmailVerificationToken(
        id=generator.next_id(),
        user_id=user.id,
        token_hash=hash_token_identifier(
            raw_token, secret=get_settings().token_hash_secret),
            expires_at=datetime.now(timezone.utc)+VERIFICATION_TOKEN_TTL,
        )
    await create_email_verification_token(session,verification_token)

    return RegistrationResult(
        user=user,
        verification_token=raw_token
    )



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
    family_id: UUID | None = None,
    parent_token_id: int | None = None,
) -> IssuedTokenPair:
    settings = get_settings()
    token_family_id = family_id or uuid4()

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
        family_id=token_family_id,
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
        family_id=token_family_id,
        parent_token_id=parent_token_id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(seconds=settings.refresh_token_ttl_seconds),
    )
    await create_refresh_token_record(session, refresh_record)

    return IssuedTokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_ttl_seconds,
    )

async def rotate_refresh_token(
    *,
    session: AsyncSession,
    refresh_token:str,
    generator:SnowflakeGenerator,
)->IssuedTokenPair:
    settings=get_settings()
    now=datetime.now(timezone.utc)

    try:
        claims=decode_refresh_token(
            refresh_token,
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience
        )
        user_id=int(str(claims["sub"]))
        family_id=UUID(str(claims["family_id"]))
        token_hash=hash_token_identifier(str(claims["jti"]),
                                         secret=settings.token_hash_secret,
                                         )
    except (InvalidRefreshJwtError, KeyError, TypeError, ValueError) as error:
        raise InvalidRefreshTokenError from error

    token_record=await get_refresh_token_by_token_hash_for_update(
        session,
        token_hash,
    )

    if( # Ensure the refresh token still represents a valid, active login session.
        token_record is None
        or token_record.user_id!=user_id
        or token_record.family_id!=family_id
        or token_record.expires_at<=now
        or token_record.revoked_at is not None
    ):
        raise InvalidRefreshTokenError

# A refresh token is single-use. Reusing an already-consumed token indicates
# a replay attack, so revoke the entire refresh-token family.
    if token_record.used_at is not None:
        await revoke_refresh_token_family(
            session,
            family_id=token_record.family_id,
            revoked_at=now,
        )
        raise InvalidRefreshTokenError
    # Ensure the owning account still exists and is eligible to receive new
    # tokens.
    user = await get_user_by_id(session, token_record.user_id)
    if user is None or user.email_verified_at is None:
        raise InvalidRefreshTokenError

    token_record.used_at = now # Consume this refresh token so it can never be used again.

    # Rotate the refresh token by issuing a new token pair in the same family.
    # The parent_token_id links the new refresh token to the one it replaced.
    return await issue_token_pair(
        session=session,
        user=user,
        generator=generator,
        family_id=token_record.family_id,
        parent_token_id=token_record.id,
    )



# A refresh-token family represents one authenticated login session.
#
# • Login:
#   - A successful login creates a brand-new `family_id` (UUID), a new access
#     token, and the first refresh token in that family.
#
# • Refresh rotation:
#   - Access tokens are short-lived (e.g. 15 minutes). When one expires, the
#     client presents its current refresh token instead of logging in again.
#   - Refresh tokens have a maximum lifetime (e.g. 30 days) but are single-use.
#     Every successful refresh marks the current refresh token as used and
#     issues a new access token and a new refresh token with a fresh expiry.
#   - The new refresh token reuses the same `family_id`, so all rotated refresh
#     tokens belong to the same login session. `parent_token_id` links each
#     refresh token to the one that created it.
#
# • Session end:
#   - If the session ends normally (logout or refresh-token expiry), the next
#     login starts a completely new refresh-token family with a new UUID.
#   - Previous families are never reused or linked to new ones; they may remain
#     in the database for auditing or later cleanup.
#
# • Replay protection:
#   - Reusing an already-consumed refresh token indicates a possible replay
#     attack. The server revokes every refresh token in that family, invalidating
#     the entire login session.
#   - The user must log in again, creating a new token pair in a brand-new,
#     unrelated refresh-token family.

class InvalidOrExpiredTokenError(Exception):
    pass
async def verify_email(
        *, #Everything after this is keyword-only
        session:AsyncSession,
        token:str,
)->User:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    token_hash = hash_token_identifier(
        token,
        secret=settings.token_hash_secret,
    )
    token_record = await get_email_verification_token_by_hash_for_update(
            session,
            token_hash,
        )
    if (
            token_record is None
            or token_record.consumed_at is not None
            or token_record.expires_at <= now
        ):
            raise InvalidOrExpiredTokenError
    
    user = await get_user_by_id(session, token_record.user_id)
    if user is None:
        raise InvalidOrExpiredTokenError

    token_record.consumed_at = now
    user.email_verified_at = now
    
    return user

async def logout_refresh_token(
        *,
        session:AsyncSession,
        refresh_token: str,
        )->None:
    settings=get_settings()
    try:
        claims=decode_refresh_token(
            refresh_token,
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience
        )
        token_hash = hash_token_identifier(
            str(claims["jti"]),
            secret=settings.token_hash_secret,
        )
    except (InvalidRefreshJwtError, KeyError, TypeError) as error:
        raise InvalidRefreshTokenError from error

    token_record=await get_refresh_token_by_token_hash_for_update(
        session,
        token_hash,
    )
    if token_record is None:
        raise InvalidRefreshTokenError

    await revoke_refresh_token_family(
        session,
        family_id=token_record.family_id,
        revoked_at=datetime.now(timezone.utc)
        )

PASSWORD_RESET_TOKEN_TTL=timedelta(hours=1)

@dataclass
class PasswordResetRequestResult:
    user:User
    reset_token:str
    token_id:int

async def request_password_reset(
        *, #Everything after * must be passed by keyword.
        session:AsyncSession,
        email:str,
        generator:SnowflakeGenerator,
)->PasswordResetRequestResult|None:
    user=await get_user_by_email(
        session,
        normalize_email(email),
    )    
#If the account doesn't exist or doesn't have a local password, don't create a password-reset token.
    if user is None or user.password_hash is None:
        return None

    raw_token=generate_opaque_token()
    token=PasswordResetToken(
        id=generator.next_id(),
        user_id=user.id,
        token_hash=hash_token_identifier(
            raw_token,secret=get_settings().token_hash_secret,),
            expires_at=datetime.now(timezone.utc)+PASSWORD_RESET_TOKEN_TTL,)

    await create_password_reset_token(session, token)

    return PasswordResetRequestResult(
        user=user,
        reset_token=raw_token,
        token_id=token.id
    )