# Persistence for the planned Google OpenID Connect (OIDC) authorization flow.
# A table record does not implement callback validation or browser binding.
# State correlates a callback with the browser session that started it.
# State helps resist login CSRF (cross-site request forgery).
# Nonce binds Google's ID token to this authentication request.
# PKCE (Proof Key for Code Exchange) requires the original verifier at exchange.
# The S256 challenge is Base64url(SHA256(ASCII(verifier))), without padding.
# Send the public challenge during authorization. Keep the verifier secret.
# Google returns a short-lived authorization code to the registered callback.
# The target checks state, browser binding, expiry, and prior consumption.
# Exchange the code with the verifier, then validate the ID token and nonce.
# Expiry limits abandoned requests. consumed_at prevents reuse of this attempt.
# Google authorization codes also have a single-use provider lifecycle.
# Browser-binding transport and frontend token delivery remain unspecified.
# See docs/superpowers/specs/2026-08-01-authentication-authorization-design.md.

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
