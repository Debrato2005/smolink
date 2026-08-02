from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class AuthIdentity(Base):
    __tablename__="auth_identities"
    __table_args__ = (UniqueConstraint("provider", "provider_subject"),)
# __table_args__ defines table-level configuration such as composite unique
# constraints, indexes, and check constraints. Here, UniqueConstraint("provider",
# "provider_subject") ensures that the same authentication provider identity
# (e.g. Google subject ID) cannot be linked to more than one user, while still
# allowing the same provider_subject value to exist under different providers.
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
    provider: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    provider_subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )