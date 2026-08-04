from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken

from uuid import UUID
from datetime import datetime

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
# Fetch and lock the refresh-token row for this transaction. `FOR UPDATE`
# prevents concurrent refresh requests from simultaneously rotating the same
# token, ensuring only one request can consume it successfully.

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




# Refresh token rotation flow:
#
# Login:
#   - User authenticates with email/password.
#   - Server issues a new access token (short-lived) and a new refresh token
#     (long-lived), starting a new refresh-token family.
#
# Refresh:
#   - When the access token expires, the client sends the current refresh token.
#   - The server decodes the JWT claims (sub, family_id, jti), hashes the jti,
#     and looks up the corresponding database record.
#   - The refresh token must exist, belong to the correct user/family, not be
#     expired, revoked, or previously used.
#   - The token is marked as used and rotated into a brand-new refresh token
#     (same family) plus a new access token.
#
# Replay protection:
#   - A refresh token is single-use. If a previously used refresh token is ever
#     presented again, it indicates a possible token theft/replay attack.
#   - The server immediately revokes the entire refresh-token family so neither
#     the attacker nor the legitimate client can continue using any descendant
#     refresh tokens. The user must authenticate again.
#
# Lifetime:
#   - Access tokens are short-lived (e.g. 15 minutes) and are never reused.
#   - Refresh tokens have a maximum lifetime (e.g. 30 days), but in normal use
#     they are consumed long before expiry because each successful refresh
#     replaces them with a new refresh token.

# Fetch and lock the refresh-token row for this transaction. `FOR UPDATE`
# prevents concurrent refresh requests from simultaneously rotating the same
# token, ensuring only one request can consume it successfully.

# Revoke every active refresh token in the same token family. This is used when
# a replay attack is detected (a previously consumed refresh token is reused),
# ensuring no descendant refresh tokens in that session remain valid.

# Normal refresh rotation marks only the presented refresh token as `used_at`
# and issues a new active refresh token in the same family. The family is
# revoked (`revoked_at`) only if a previously used token is seen again,
# indicating a replay attack or other session compromise.

