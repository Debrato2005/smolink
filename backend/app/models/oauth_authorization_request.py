from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OAuthAuthorizationRequest(Base):
    __tablename__ = "oauth_authorization_requests"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
    )
    state_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )
    nonce: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    pkce_verifier: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )