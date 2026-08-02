from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(BigInteger, 
                                  primary_key=True, 
                                  autoincrement=False, #false when distributed
                                  )
    email: Mapped[str]=mapped_column(String(320), #bcz max 320 chars is standard
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
    
# password_hash is nullable because not every user authenticates with a local
# password. Users who sign in only through Google OAuth2/OIDC won't have a
# password hash stored. Local accounts require a password_hash; Google-only
# accounts can legitimately have NULL.