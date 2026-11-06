# PyJWT signs Header.Payload with HS256 and validates the token on decode.
# Header, payload, and signature use Base64url encoding in the JWT format.
# The signature detects changes under the configured secret. It does not encrypt.
# Claims remain readable. Keep passwords and other secrets out of them.
# Required claims and typ distinguish access JWTs from refresh JWTs.
# JWT signing and persistence hashing have separate purposes and secrets.
# hash_token_identifier() hashes refresh jti or an entire opaque token value.
# Hash the presented value with the same key to find its stored record.
# `*` makes the following parameters keyword-only to avoid argument-order errors.

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

import hashlib
import hmac

import secrets

password_hasher=PasswordHasher()

def hash_password(password:str)->str:
    return password_hasher.hash(password)

def verify_password(password:str,password_hash:str)->bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (InvalidHashError, VerificationError):
        return False

def normalize_email(email: str) -> str:
    return email.strip().lower()


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
            options={
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
    *,
    secret: str,
) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        token_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def generate_opaque_token()->str:
    return secrets.token_urlsafe(32)
