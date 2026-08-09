from html import escape 
from urllib.parse import quote

import httpx

from app.core.config import get_settings

class EmailDeliveryError(Exception):
    pass

async def send_verification_email(
        *,
        recipient_email:str,
        verification_token:str,
        idempotency_key:str,
)->None:
    settings=get_settings()

    verification_url=(
        f"{settings.app_public_url.rstrip('/')}/verify-email"
        f"#token={quote(verification_token,safe='')}"
    )
    safe_url = escape(verification_url, quote=True)
# Build the verification link using the configured public URL. URL-encode the
# verification token so every character is preserved safely in the URL fragment,
# then HTML-escape the final URL before embedding it in the email body.

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Idempotency-Key": idempotency_key,
                },
                json={
                    "from": settings.email_from,
                    "to": [recipient_email],
                    "subject": "Verify your Smolink email",
                    "html": (
                        "<p>Verify your email address:</p>"
                        f'<p><a href="{safe_url}">Verify email</a></p>'
                    ),
# Use single quotes for the Python string so the HTML can use its standard
# double-quoted attributes without requiring escape sequences (e.g. href="...").
                    "text": f"Verify your email address: {verification_url}",
                },
            )

    except httpx.HTTPError as exc:
        raise EmailDeliveryError from exc

    if response.is_error:
        raise EmailDeliveryError
