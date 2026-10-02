# Import each concrete model to register its table with Base.metadata.
# These imports also expose models through app.models.
# __all__ lists the intended public model names for wildcard imports.

from app.models.click_event import ClickEvent
from app.models.url import Url
from app.models.user import User
from app.models.auth_identity import AuthIdentity
from app.models.refresh_token import RefreshToken
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken
from app.models. oauth_authorization_request import OAuthAuthorizationRequest

__all__ = ["ClickEvent",
           "Url", "User",
           "AuthIdentity",
           "RefreshToken",
           "EmailVerificationToken",
           "PasswordResetToken",
           "OAuthAuthorizationRequest"]
