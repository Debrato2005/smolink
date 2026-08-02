from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )
    family_id: Mapped[UUID] = mapped_column(
        Uuid,
        index=True,
        nullable=False,
    )
    parent_token_id: Mapped[int | None] = mapped_column(
        ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

# RefreshToken stores long-lived refresh tokens used to obtain new JWT access
# tokens without requiring the user to log in again. Unlike access tokens,
# refresh tokens are stateful and are persisted (as hashes) so the server can
# securely manage user sessions.
#
# This table enables:
# - Refresh token rotation (issue a new refresh token on every refresh).
# - Reuse detection (detect if an already-used token is presented again,
#   indicating possible token theft).
# - Token revocation (logout, password changes, administrator actions, etc.).
# - Per-device/session management (multiple active sessions per user).
# - Expiration and lifecycle tracking for every issued refresh token.
#
# Key fields:
# - token_hash: SHA-256 hash of the refresh token; the raw token is never stored.
# - family_id: Random UUID shared by all rotated tokens originating from the
#   same login session (token family). If compromise is detected, the entire
#   family can be revoked.
# - parent_token_id: Links each rotated token to its predecessor, forming the
#   refresh-token rotation chain.
# - issued_at / expires_at: Track token lifetime.
# - used_at: Records when a refresh token has been consumed during rotation.
# - revoked_at: Marks tokens that have been explicitly invalidated.
#
# Access tokens remain short-lived and stateless (JWTs), while refresh tokens
# are intentionally stateful to provide secure long-lived authentication.