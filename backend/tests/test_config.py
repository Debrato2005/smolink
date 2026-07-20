def test_settings_reads_environment_variables(monkeypatch)-> None: #monkeypatch is a built-in pytest tool that temporarily changes environment variables only for this test.
    from app.core.config import Settings

    monkeypatch.setenv("DATABASE_URL","postgresql+asyncpg://smolink:smolink@localhost:5432/smolink")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret")
    monkeypatch.setenv("IP_HASH_SECRET", "test-ip-hash-secret")
    monkeypatch.setenv("PUBLIC_BASE_URL", "http://localhost:8000")

    settings=Settings(_env_file=None)

    assert settings.database_url == ( "postgresql+asyncpg://smolink:smolink@localhost:5432/smolink")
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.jwt_secret == "test-jwt-secret"
    assert settings.ip_hash_secret == "test-ip-hash-secret"
    assert settings.public_base_url == "http://localhost:8000"
    assert settings.redis_cache_ttl_seconds == 3600
