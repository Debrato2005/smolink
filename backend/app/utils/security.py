from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

import hashlib
import hmac

import secrets

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

class InvalidRefreshJwtError(Exception):
    pass


def create_refresh_token(
    *,
    user_id: int,
    family_id: UUID,
    secret: str,
    issuer: str,
    audience: str,
    expires_in: timedelta,
) -> str:
    now = datetime.now(timezone.utc)

    claims = {
        "sub": str(user_id),
        "family_id": str(family_id),
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "nbf": now,
        "exp": now + expires_in,
        "typ": "refresh",
        "jti": uuid4().hex,
    }

    return jwt.encode(claims, secret, algorithm="HS256")


def decode_refresh_token(
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
            options={ #These claims must exist in every valid token
                "require": [
                    "sub",
                    "family_id",
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
        raise InvalidRefreshJwtError from error

    if claims["typ"] != "refresh":
        raise InvalidRefreshJwtError

    return claims

def hash_token_identifier(
    token_id: str,
    *, #Everything after * must be passed as a keyword argument.
    secret: str,
) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        token_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

# JWT Signature Summary

# 1. Server creates:
#    Header + Payload

# 2. Server computes:
#    Signature = HMAC(Header + Payload, Secret Key)

# 3. JWT sent to client:
#    header.payload.signature

# 4. Client sends JWT back on every request.

# 5. Server verifies by:
#    - Taking the received header and payload.
#    - Recomputing the signature using its secret key.
#    - Comparing the computed signature with the received signature.

# 6. If the header or payload is modified:
#    - The recomputed signature changes completely (avalanche effect).
#    - The attacker cannot generate a new valid signature because they do not know the server's secret key.
#    - Signatures do not match → JWT is rejected.

# Key idea:
# The signature guarantees the JWT's integrity (it hasn't been tampered with) and 
# authenticity (it was signed by someone with the secret key). 
# It does NOT encrypt the payload—the header and payload remain readable by anyone.
#=================================================================================================================================
# JWTs and token hashing serve different purposes:
#
# • jwt.encode() creates a signed JWT that the client carries. It packages
#   claims (e.g. user ID, expiry, token type) into a token and signs them
#   using the server's secret. The signature lets the server detect if the
#   token was modified, but it does not hide the claims.
#
# • jwt.decode() verifies the signature and extracts the claims if the token
#   is valid.
#
# • hash_token_identifier() is unrelated to JWT signing. It hashes only the
#   refresh token's `jti` before storing it in the database, so the server
#   never stores the raw token identifier. Later, the server hashes the `jti`
#   from a presented refresh token again and compares the hash to the stored
#   value.

def generate_opaque_token()->str:
    return secrets.token_urlsafe(32)