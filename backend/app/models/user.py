# autoincrement=False requires the application to supply each ID.
# The email column allows 320 characters and has a unique index.
# Local accounts have an Argon2id password hash.
# Nullable password_hash supports planned Google-only accounts without a password.

from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(BigInteger, 
                                  primary_key=True, 
                                  autoincrement=False,
                                  )
    email: Mapped[str]=mapped_column(String(320),
                                     unique=True,
                                     index=True,
                                     nullable=False,
                                     )
    password_hash: Mapped[str]= mapped_column(String(255),
                                              nullable=True,
                                              )
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),
                                                      server_default=func.now(),
                                                      nullable=False,
                                                      )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 onupdate=func.now(),
                                                 nullable=False,
                                                 )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_count: Mapped[int] = mapped_column(
        Integer,
        server_default=text("0"),
        nullable=False,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    auth_version: Mapped[int] = mapped_column(
        Integer,
        server_default=text("1"),
        nullable=False,
    )
