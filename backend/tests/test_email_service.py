import asyncio

import pytest

from app.services.email_service import (
    EmailDeliveryError,
    send_verification_email,
)
@pytest.fixture
def fake_email_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSettings:
        resend_api_key = "test-resend-api-key"
        app_public_url = "http://localhost:8000"
        email_from = "test@example.com"

    monkeypatch.setattr(
        "app.services.email_service.get_settings",
        lambda: FakeSettings(),
    )
    
def test_send_verification_email_uses_fragment_token_and_idempotency(
    monkeypatch,
    fake_email_settings: None,
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
    assert sent["headers"]["Authorization"] == "Bearer test-resend-api-key"
    assert sent["headers"]["Idempotency-Key"] == "verification:123"
    assert sent["json"]["to"] == ["user@example.com"]
    assert "#token=token-value" in sent["json"]["text"]

def test_send_verification_email_hides_provider_failure(
    monkeypatch,
    fake_email_settings: None,
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

# Tests the password-reset email service without making a real Resend request.
# A FakeClient replaces httpx.AsyncClient and captures the outgoing URL,
# headers, and JSON payload. The test then verifies the required Resend
# headers and that the reset token is URL-encoded inside the URL fragment.
# @pytest.mark.asyncio lets the test directly await the async email service.
@pytest.mark.asyncio
async def test_send_password_reset_email_uses_fragment_token(
    monkeypatch:pytest.MonkeyPatch,
    fake_email_settings: None,
)->None:
    sent:dict[str,object]={}

    class FakeResponse:
        is_error=False

    class FakeClient:
        async def __aenter__(self)->"FakeClient":
            return self
        async def __aexit__(self,*args:object)->None: 
            return None
        async def post(self,url:str,**kwargs:object)->FakeResponse:
            sent["url"]=url
            sent.update(kwargs)
            return FakeResponse()

    monkeypatch.setattr(
        "app.services.email_service.httpx.AsyncClient",
        lambda **_: FakeClient(),
    )
# The real API key was exposed because the test only mocked the HTTP client,
# not the application's settings. get_settings() therefore loaded the real
# RESEND_API_KEY from .env, the email service put it in the Authorization
# header, and the FakeClient captured it in `sent`, which pytest printed when
# the assertion failed. FakeSettings must replace get_settings() as well.
    from app.services.email_service import send_password_reset_email

    await send_password_reset_email(
        recipient_email="user@example.com",
        reset_token="reset token",
        idempotency_key="reset:123",
    )

    assert sent["headers"]== {
        "Authorization": "Bearer test-resend-api-key",
        "Idempotency-Key": "reset:123",
    }
    assert "#token=reset%20token" in str(sent["json"])
    
