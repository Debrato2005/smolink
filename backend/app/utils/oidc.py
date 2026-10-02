import base64
import hashlib
import secrets

def create_pkce_verifier() -> str:
    # Generate a cryptographically secure random value for one OAuth login.
    #
    # token_urlsafe() produces URL-safe Base64 characters such as:
    #
    #     A-Z a-z 0-9 - _
    #
    # These are valid RFC 7636 PKCE verifier characters.
    #
    # 64 random bytes encode to about 86 characters, which is within
    # PKCE's required verifier length of 43-128 characters.
    return secrets.token_urlsafe(64)
