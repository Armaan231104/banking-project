from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Banking API'
    env: str = 'dev'
    database_url: str = 'sqlite:///./banking.db'
    jwt_secret: str = 'change-me'
    jwt_algorithm: str = 'HS256'
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    fraud_threshold: float = 10000
    redis_url: str = 'redis://localhost:6379/0'
    login_rate_limit_per_minute: int = 10
    aws_region: str | None = None
    s3_bucket: str | None = None
    s3_prefix: str = 'statements'
    aws_access_key_id: str | None = Field(default=None)
    aws_secret_access_key: str | None = Field(default=None)


@lru_cache
def get_settings() -> Settings:
    return Settings()
