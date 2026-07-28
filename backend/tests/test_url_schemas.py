from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from app.schemas.url import CreateUrlRequest, CreateUrlResponse


def test_create_url_request_accepts_optional_values() -> None:
    request = CreateUrlRequest(
        destination="https://example.com/path",
        alias="my-link",
        expires_at="2030-01-01T00:00:00Z",
    )

    assert str(request.destination) == "https://example.com/path"
    assert request.alias == "my-link"
    assert request.expires_at is not None


def test_create_url_request_rejects_invalid_destination() -> None:
    with pytest.raises(ValidationError):
        CreateUrlRequest(destination="not-a-url")


def test_create_url_response_exposes_public_link_data() -> None:
    response = CreateUrlResponse(
        id=1,
        short_code="abc123",
        short_url="http://localhost:8000/abc123",
        destination="https://example.com",
        expires_at=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    assert response.short_code == "abc123"
    assert response.expires_at is None