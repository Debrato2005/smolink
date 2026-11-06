# BaseSettings loads typed fields from environment variables and .env.
# Fields without defaults are required. The .env path is working-directory-relative.
# lru_cache retains the first settings instance for subsequent calls.

from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# HMAC and HS256 keys shorter than 32 characters are guessable; equal keys would merge separate purposes.
MIN_SECRET_LENGTH = 32

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret: str
    ip_hash_secret: str
    public_base_url: str
    redis_cache_ttl_seconds: int = 3600

    jwt_issuer: str
    jwt_audience: str
    access_token_ttl_seconds: int
    refresh_token_ttl_seconds: int
    token_hash_secret: str

    snowflake_worker_id: int = 0

    app_public_url: str
    email_from: str
    resend_api_key: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str 

    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
        )

    @field_validator("jwt_secret", "token_hash_secret", "ip_hash_secret")
    @classmethod
    def _secret_is_long_enough(cls, value: str) -> str:
        if len(value) < MIN_SECRET_LENGTH:
            raise ValueError(f"must be at least {MIN_SECRET_LENGTH} characters")
        return value

    @model_validator(mode="after")
    def _secrets_are_distinct(self) -> "Settings":
        if len({self.jwt_secret, self.token_hash_secret, self.ip_hash_secret}) != 3:
            raise ValueError("JWT_SECRET, TOKEN_HASH_SECRET and IP_HASH_SECRET must differ")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()
