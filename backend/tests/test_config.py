def test_settings_reads_environment_variables(monkeypatch)-> None: #monkeypatch is a built-in pytest tool that temporarily changes environment variables only for this test.
    from app.core.config import Settings

    monkeypatch.setenv("DATABASE_URL","postgresql+asyncpg://smolink:smolink@localhost:5432/smolink")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret")
    monkeypatch.setenv("IP_HASH_SECRET", "test-ip-hash-secret")
    monkeypatch.setenv("PUBLIC_BASE_URL", "http://localhost:8000")

    monkeypatch.setenv("JWT_ISSUER", "smolink")
    monkeypatch.setenv("JWT_AUDIENCE", "smolink-api")
    monkeypatch.setenv("ACCESS_TOKEN_TTL_SECONDS", "900")
    monkeypatch.setenv("REFRESH_TOKEN_TTL_SECONDS", "2592000")
    monkeypatch.setenv("TOKEN_HASH_SECRET", "test-token-hash-secret")

    monkeypatch.setenv("APP_PUBLIC_URL", "http://localhost:3000")
    monkeypatch.setenv(
            "EMAIL_FROM",
        "Smolink <noreply@example.com>", )
    monkeypatch.setenv("RESEND_API_KEY", "re_test_key")

    settings=Settings(_env_file=None)

    assert settings.database_url == ( "postgresql+asyncpg://smolink:smolink@localhost:5432/smolink")
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.jwt_secret == "test-jwt-secret"
    assert settings.ip_hash_secret == "test-ip-hash-secret"
    assert settings.public_base_url == "http://localhost:8000"
    assert settings.redis_cache_ttl_seconds == 3600

    assert settings.snowflake_worker_id == 0

    assert settings.jwt_issuer == "smolink"
    assert settings.jwt_audience == "smolink-api"
    assert settings.access_token_ttl_seconds == 900
    assert settings.refresh_token_ttl_seconds == 2_592_000
    assert settings.token_hash_secret == "test-token-hash-secret"

    assert settings.app_public_url == "http://localhost:3000"
    assert settings.email_from == "Smolink <noreply@example.com>"
    assert settings.resend_api_key == "re_test_key"