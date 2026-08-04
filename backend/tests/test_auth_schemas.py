import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, TokenPairResponse, RefreshRequest

def test_login_request_accepts_valid_credentials() -> None:
    request=LoginRequest(
        email="User@Example.COM",
        password="hello12345678",
    )

    assert str(request.email) == "User@example.com"
    assert request.password == "hello12345678"

@pytest.mark.parametrize( #Instead of writing three separate tests, pytest runs the same test with three different inputs.
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
        LoginRequest(**payload) #The ** operator unpacks the dictionary into keyword arguments.

# `**` unpacks a dictionary into keyword arguments. For example:
#
#     payload = {"email": "...", "password": "..."}
#
#     LoginRequest(**payload)
#
# is equivalent to:
#
#     LoginRequest(
#         email="...",
#         password="...",
#     )
#
# Without `**`, the entire dictionary would be passed as a single positional
# argument, which is not how Pydantic BaseModels are constructed.

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


def test_refresh_request_requires_a_token() -> None:
    request = RefreshRequest(refresh_token="refresh-token")

    assert request.refresh_token == "refresh-token"

    with pytest.raises(ValidationError):
        RefreshRequest(refresh_token="")
