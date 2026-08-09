import asyncio

import pytest

from app.services.email_service import (
    EmailDeliveryError,
    send_verification_email,
)

def test_send_verification_email_uses_fragment_token_and_idempotency(
    monkeypatch,
) -> None:
    sent: dict[str, object] = {}

    class FakeResponse:
        is_error=False

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return None

        async def post(self, url, *, headers, json):
            sent["url"] = url
            sent["headers"] = headers
            sent["json"] = json
            return FakeResponse()
    monkeypatch.setattr(
                    "app.services.email_service.httpx.AsyncClient",
                    lambda *, timeout: FakeClient(),
                )
    asyncio.run(
            send_verification_email(
                recipient_email="user@example.com",
                verification_token="token-value",
                idempotency_key="verification:123",
            )
        )
    
    assert sent["url"] == "https://api.resend.com/emails"
    assert sent["headers"]["Idempotency-Key"] == "verification:123"
    assert sent["json"]["to"] == ["user@example.com"]
    assert "#token=token-value" in sent["json"]["text"]

def test_send_verification_email_hides_provider_failure(
    monkeypatch,
) -> None:
    class FakeResponse:
        is_error = True

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return None

        async def post(self, url, *, headers, json):
            return FakeResponse()

    monkeypatch.setattr(
        "app.services.email_service.httpx.AsyncClient",
        lambda *, timeout: FakeClient(),
    )

    with pytest.raises(EmailDeliveryError):
        asyncio.run(
            send_verification_email(
                recipient_email="user@example.com",
                verification_token="token-value",
                idempotency_key="verification:123",
            )
        )