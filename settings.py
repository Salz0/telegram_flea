"""The module for the settings of the application."""
import os

from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Settings for the Telegram bot."""

    TELEGRAM_BOT_TOKEN: str

    class Config:
        """Configuration for the settings."""

        env_file = ".env"


settings = Settings()
if os.environ.get("DATABASE_URL"):
    settings.DATABASE_URL = os.environ.get("DATABASE_URL")
if os.environ.get("REDIS_URL"):
    settings.DATABASE_URL = os.environ.get("REDIS_URL")
