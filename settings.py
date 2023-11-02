"""The module for the settings of the application."""
from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Settings for the Telegram bot."""

    TELEGRAM_BOT_TOKEN: str

    class Config:
        """Configuration for the settings."""

        env_file = ".env"


settings = Settings()
