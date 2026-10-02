# token_hash stores a keyed HMAC-SHA256 hash of the refresh JWT jti.
# The raw refresh JWT and raw identifier are not stored.
# family_id groups records from one login. parent_token_id links each successor.
# issued_at/expires_at track lifetime. used_at records rotation consumption.
# revoked_at blocks future refreshes from an explicitly revoked record.
# Reuse of a consumed token revokes the family's active records.
# Multiple logins can create independent families for one user.
# Each rotation gives its successor a fresh expiry, not an absolute family expiry.
# Access JWTs have no row per token. Current-user checks still query PostgreSQL.
# Logout blocks refreshes. Password reset also invalidates access via auth_version.

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
    # Keyed hash of jti, not the complete refresh JWT.
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
