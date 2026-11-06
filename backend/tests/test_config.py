# monkeypatch restores environment changes after this test.
# _env_file=None excludes local developer configuration from Settings.

import pytest
from pydantic import ValidationError

JWT_SECRET = "test-jwt-secret-0123456789abcdef-0001"
IP_HASH_SECRET = "test-ip-hash-secret-0123456789abcdef-02"
TOKEN_HASH_SECRET = "test-token-hash-secret-0123456789abcd-03"

def test_settings_reads_environment_variables(monkeypatch)-> None:
    from app.core.config import Settings

    monkeypatch.setenv("DATABASE_URL","postgresql+asyncpg://smolink:smolink@localhost:5432/smolink")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("IP_HASH_SECRET", IP_HASH_SECRET)
    monkeypatch.setenv("PUBLIC_BASE_URL", "http://localhost:8000")

    monkeypatch.setenv("JWT_ISSUER", "smolink")
    monkeypatch.setenv("JWT_AUDIENCE", "smolink-api")
    monkeypatch.setenv("ACCESS_TOKEN_TTL_SECONDS", "900")
    monkeypatch.setenv("REFRESH_TOKEN_TTL_SECONDS", "2592000")
    monkeypatch.setenv("TOKEN_HASH_SECRET", TOKEN_HASH_SECRET)

    monkeypatch.setenv("APP_PUBLIC_URL", "http://localhost:3000")
    monkeypatch.setenv(
            "EMAIL_FROM",
        "Smolink <noreply@example.com>", )
    monkeypatch.setenv("RESEND_API_KEY", "re_test_key")

    monkeypatch.setenv("GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "google-client-secret")
    monkeypatch.setenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/api/v1/auth/google/callback",
)

    settings=Settings(_env_file=None)

    assert settings.database_url == ( "postgresql+asyncpg://smolink:smolink@localhost:5432/smolink")
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.jwt_secret == JWT_SECRET
    assert settings.ip_hash_secret == IP_HASH_SECRET
    assert settings.public_base_url == "http://localhost:8000"
    assert settings.redis_cache_ttl_seconds == 3600

    assert settings.snowflake_worker_id == 0

    assert settings.jwt_issuer == "smolink"
    assert settings.jwt_audience == "smolink-api"
    assert settings.access_token_ttl_seconds == 900
    assert settings.refresh_token_ttl_seconds == 2_592_000
    assert settings.token_hash_secret == TOKEN_HASH_SECRET

    assert settings.app_public_url == "http://localhost:3000"
    assert settings.email_from == "Smolink <noreply@example.com>"
    assert settings.resend_api_key == "re_test_key"

    assert settings.google_client_id == "google-client-id"
    assert settings.google_client_secret == "google-client-secret"
    assert settings.google_redirect_uri == (
    "http://localhost:8000/api/v1/auth/google/callback"
)


def _set_required(monkeypatch, **overrides) -> None:
    values = {
        "DATABASE_URL": "postgresql+asyncpg://smolink:smolink@localhost:5432/smolink",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_SECRET": JWT_SECRET,
        "IP_HASH_SECRET": IP_HASH_SECRET,
        "TOKEN_HASH_SECRET": TOKEN_HASH_SECRET,
        "PUBLIC_BASE_URL": "http://localhost:8000",
        "JWT_ISSUER": "smolink",
        "JWT_AUDIENCE": "smolink-api",
        "ACCESS_TOKEN_TTL_SECONDS": "900",
        "REFRESH_TOKEN_TTL_SECONDS": "2592000",
        "APP_PUBLIC_URL": "http://localhost:3000",
        "EMAIL_FROM": "Smolink <noreply@example.com>",
        "RESEND_API_KEY": "re_test_key",
        "GOOGLE_CLIENT_ID": "google-client-id",
        "GOOGLE_CLIENT_SECRET": "google-client-secret",
        "GOOGLE_REDIRECT_URI": "http://localhost:8000/api/v1/auth/google/callback",
    }
    values.update(overrides)
    for name, value in values.items():
        monkeypatch.setenv(name, value)


@pytest.mark.parametrize("name", ["JWT_SECRET", "TOKEN_HASH_SECRET", "IP_HASH_SECRET"])
def test_short_secrets_are_rejected_without_echoing_them(monkeypatch, name) -> None:
    from app.core.config import Settings

    short = "short-secret-value"
    _set_required(monkeypatch, **{name: short})
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)
    assert "at least 32 characters" in str(error.value)
    assert short not in str(error.value)


def test_reused_secrets_are_rejected(monkeypatch) -> None:
    from app.core.config import Settings

    _set_required(monkeypatch, TOKEN_HASH_SECRET=JWT_SECRET)
    with pytest.raises(ValidationError, match="must differ"):
        Settings(_env_file=None)

