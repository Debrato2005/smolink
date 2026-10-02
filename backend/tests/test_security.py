# Argon2id uses a random salt and configurable memory/work parameters.
# The stored hash includes the algorithm, parameters, salt, and hash value.
# Library verification checks the candidate password against that stored value.
# Tests require distinct hashes for the same password and reject wrong passwords.
# Token-type tests reject an access JWT where a refresh JWT is required.

from app.utils.security import hash_password, verify_password

from app.utils.security import hash_password, normalize_email, verify_password

from datetime import timedelta

import pytest

from app.utils.security import InvalidAccessTokenError, create_access_token, decode_access_token, InvalidRefreshJwtError,create_refresh_token,decode_refresh_token,generate_opaque_token

from uuid import UUID, uuid4

def test_password_hash_is_argon2id_and_verifiable()->None:
    password="hello1345678"
    password_hash=hash_password(password)

    assert password_hash!=password
    assert password_hash.startswith("$argon2id$")
    assert verify_password(password,password_hash)
    assert not verify_password("wrong12345678",password_hash)

def test_normalize_email_strips_and_lowercases() -> None:
    assert normalize_email(" User.Name@Example.COM ") == "user.name@example.com"


def test_access_token_contains_only_required_claims()->None:
    token=create_access_token(
        user_id=123,
        auth_version=1,
        secret="test-jwt-secret",
        issuer="smolink",
        audience="smolink-api",
        expires_in=timedelta(minutes=15),
    )
    claims=decode_access_token(
        token,
        secret="test-jwt-secret",
        issuer="smolink",
        audience="smolink-api",
    )
    assert claims["sub"] == "123"
    assert claims["auth_version"] == 1
    assert claims["typ"] == "access"
    assert isinstance(claims["jti"], str)
    assert "email" not in claims
    assert "password" not in claims

def test_access_token_rejects_wrong_issuer_or_audience() -> None:
    token = create_access_token(
        user_id=123,
        auth_version=1,
        secret="test-jwt-secret",
        issuer="smolink",
        audience="smolink-api",
        expires_in=timedelta(minutes=15),
    )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(
            token,
            secret="test-jwt-secret",
            issuer="wrong-issuer",
            audience="smolink-api",
        )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(
            token,
            secret="test-jwt-secret",
            issuer="smolink",
            audience="wrong-audience",
        )


def test_refresh_token_contains_required_sesssiion_claims()->None:
    family_id=uuid4()

    token=create_refresh_token(
        user_id=123,
        family_id=family_id,
        secret="test-jwt-secret",
        issuer="smolink",
        audience="smolink-api",
        expires_in=timedelta(days=30),
    )

    claims = decode_refresh_token(
        token,
        secret="test-jwt-secret",
        issuer="smolink",
        audience="smolink-api",
    )

    assert claims["sub"] == "123"
    assert claims["typ"] == "refresh"
    assert UUID(str(claims["family_id"])) == family_id
    assert isinstance(claims["jti"], str)
    assert "email" not in claims
    assert "password" not in claims

def test_refresh_decoder_rejects_access_token() -> None:
    access_token = create_access_token(
        user_id=123,
        auth_version=1,
        secret="test-jwt-secret",
        issuer="smolink",
        audience="smolink-api",
        expires_in=timedelta(minutes=15),
    )

    with pytest.raises(InvalidRefreshJwtError):
        decode_refresh_token(
            access_token,
            secret="test-jwt-secret",
            issuer="smolink",
            audience="smolink-api",
        )

def test_generate_opaque_token_returns_unique_nonempty_values() -> None:
    first = generate_opaque_token()
    second = generate_opaque_token()

    assert first
    assert second
    assert first != second
