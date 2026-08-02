import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, TokenPairResponse

def test_login_request_accepts_valid_credentials() -> None:
    request=LoginRequest(
        email="User@Example.COM",
        password="hello12345678",
    )

    assert str(request.email) == "User@example.com"
    assert request.password == "hello12345678"

@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "hello12345678"},
        {"email": "user@example.com", "password": "too-short"},
        {"email": "user@example.com", "password": "x" * 129},
    ],
)
def test_login_request_rejects_invalid_credentials(
    payload: dict[str, str],
) -> None:
    with pytest.raises(ValidationError):
        LoginRequest(**payload)

def test_token_pair_response_has_the_public_contract() -> None:
    response = TokenPairResponse(
        access_token="access-token",
        refresh_token="refresh-token",
        expires_in=900,
    )

    assert response.model_dump() == {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "token_type": "bearer",
        "expires_in": 900,
    }