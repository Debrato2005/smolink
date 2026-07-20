from functools import lru_cache #Imports Python’s cache decorator. It will let the app create one settings object and reuse it.

from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings): #Defines your application settings. Because it inherits BaseSettings, values come from environment variables or .env, not hardcoded Python values.
    database_url: str
    redis_url: str
    jwt_secret: str
    ip_hash_secret: str
    public_base_url: str
    redis_cache_ttl_seconds: int = 3600

    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        )
    
@lru_cache #Caches the result of the next function. This prevents repeatedly reading environment variables for every request.
def get_settings() -> Settings:
    return Settings()