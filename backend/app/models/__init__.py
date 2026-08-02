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

# __init__.py marks this directory as a Python package and defines its public
# API by re-exporting commonly used model classes. This allows imports such as
# `from app.models import User, Url, AuthIdentity` instead of importing each
# model from its individual module. The __all__ list documents which models are
# intended to be publicly exposed by the package.