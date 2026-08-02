from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

password_hasher=PasswordHasher() #object

def hash_password(password:str)->str:
    return password_hasher.hash(password)

def verify_password(password:str,password_hash:str)->bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (InvalidHashError, VerificationError):
        return False

def normalize_email(email: str) -> str:
    return email.strip().lower()

#jwt implementation

class InvalidAccessTokenError(Exception):
    pass

def create_access_token(
    *,
    user_id: int,
    auth_version: int,
    secret: str,
    issuer: str,
    audience: str,
    expires_in: timedelta,
) -> str:
#The * means you must pass arguments using key=value (keyword arguments), not just values in order.
# `*` makes all following parameters keyword-only. This prevents accidentally
# passing many similarly-typed arguments (e.g. secret, issuer, audience) in the
    now = datetime.now(timezone.utc)
    claims = {
        "sub": str(user_id),
        "auth_version": auth_version,
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "nbf": now,
        "exp": now + expires_in,
        "typ": "access",
        "jti": uuid4().hex,
    }

    return jwt.encode(claims, secret, algorithm="HS256")

def decode_access_token(
    token: str,
    *,
    secret: str,
    issuer: str,
    audience: str,
) -> dict[str, object]:
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            issuer=issuer,
            audience=audience,
            options={
                "require": [
                    "sub",
                    "auth_version",
                    "iss",
                    "aud",
                    "exp",
                    "nbf",
                    "typ",
                    "jti",
                ],
            },
        )
    except jwt.PyJWTError as error:
        raise InvalidAccessTokenError from error

    if claims["typ"] != "access":
        raise InvalidAccessTokenError

    return claims

# wrong order, making calls safer, clearer, and more self-documenting.
# A JWT consists of three Base64URL-encoded parts:
#
#   Header.Payload.Signature
#
# Header:
#   - Created automatically by PyJWT.
#   - Specifies metadata such as the signing algorithm (e.g. HS256) and token
#     type (JWT).
#
# Payload:
#   - Provided by the application.
#   - Contains the JWT claims (e.g. sub, exp, iss, aud, auth_version, jti).
#
# Signature:
#   - Generated automatically by PyJWT by signing:
#
#         Base64URL(Header) + "." + Base64URL(Payload)
#
#     using the configured secret/private key and algorithm.
#
# During decoding, PyJWT splits the token into its three parts, verifies the
# signature, validates claims such as exp, iss, and aud, and returns the
# payload if everything is valid. Using PyJWT avoids implementing security-
# critical JWT encoding, signing, and validation logic manually.

