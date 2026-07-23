import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

env_file = os.getenv('ENV_FILE')

if env_file:
    ENV_PATH = Path(env_file)
else:
    ENV_PATH = BASE_DIR / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore',
    )

    DEBUG: bool = False
    ENVIRONMENT: Literal['development', 'test', 'production'] = 'development'

    DATABASE_URL: str
    SECRET_KEY: str

    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 15

    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_RECYCLE: int = 1800
    POOL_TIMEOUT: int = 30


@lru_cache
def get_settings() -> Settings:
    """Retrieve cached application settings."""
    return Settings()  # pyright: ignore[reportCallIssue]
