# Repositories issue SQL and flush pending changes without commit.
# session.add() registers a model. flush() sends its INSERT in the transaction.
# FOR UPDATE serializes consumption of the same token row within transactions.
# Rotation sets used_at and creates a child through the service.
# Family revocation sets revoked_at on active records in one family.
# Password reset revokes active records across all of the user's families.
# Access JWTs can be reused until expiry or an auth_version change.

from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken

from uuid import UUID
from datetime import datetime

from app.models.email_verification_token import EmailVerificationToken

from app.models.password_reset_token import PasswordResetToken

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

async def get_refresh_token_by_token_hash_for_update(
    session:AsyncSession,
    token_hash:str,
)->RefreshToken|None:
    result=await session.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash==token_hash)
        .with_for_update()
    )
    return result.scalar_one_or_none()

async def revoke_refresh_token_family(
        session:AsyncSession,
        family_id:UUID,
        revoked_at:datetime,
)->None:
    await session.execute(
        update(RefreshToken).where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=revoked_at)
    )


async def create_email_verification_token(
    session: AsyncSession,
    token: EmailVerificationToken,
) -> EmailVerificationToken:
    session.add(token)
    await session.flush()
    return token


async def get_email_verification_token_by_hash_for_update(
    session: AsyncSession,
    token_hash: str,
) -> EmailVerificationToken | None:
    result = await session.execute(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.token_hash == token_hash)
        .with_for_update()
    )
    return result.scalar_one_or_none()


async def create_password_reset_token(
        session:AsyncSession,
        token:PasswordResetToken,
)->PasswordResetToken:
    session.add(token)
    await session.flush()
    return token

async def get_password_reset_token_by_hash_for_update(
        session:AsyncSession,
        token_hash:str,
)->PasswordResetToken|None:
    result=await session.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.token_hash==token_hash)
        .with_for_update()
    )
    return result.scalar_one_or_none()

async def revoke_all_refresh_token_families(
        session:AsyncSession,
        *,
        user_id:int,
        revoked_at:datetime,
)->None:
    await session.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id==user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=revoked_at)
    )

async def consume_active_email_verification_tokens(
        session:AsyncSession,
        *,
        user_id:int,
        consumed_at:datetime
)->None:
    await session.execute(update(EmailVerificationToken)
                          .where(EmailVerificationToken.user_id==user_id,
                                 EmailVerificationToken.consumed_at.is_(None),)
                                 .values(consumed_at=consumed_at))
