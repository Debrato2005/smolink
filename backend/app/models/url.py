from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(
        BigInteger,  #snowflake 
        primary_key=True,
        autoincrement=False, #So id is the internal numeric identifier; short_code is the public redirect value. We store both because aliases cannot be derived from the ID, and redirects query short_code directly.
    )
    short_code: Mapped[str] = mapped_column(
        String(64), #snowflake+base62(on url_id)
        unique=True,
        index=True,
        nullable=False,
    )
    destination: Mapped[str] = mapped_column( #destination is simply the long/original URL.
        String(2048),
        nullable=False,
    )
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    total_clicks: Mapped[int] = mapped_column(
        Integer,
        server_default=text("0"),
        nullable=False,
    )
    last_clicked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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