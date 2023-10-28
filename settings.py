"""The module for the settings of the application."""

from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Settings for the Telegram bot."""

    # TODO: [28.10.2023 by Mykola] Should we use per-user language instead of global?
    BOT_LANGUAGE: str = "en"

    TELEGRAM_BOT_TOKEN: str

    DATABASE_URL: PostgresDsn | None
    REDIS_URL: RedisDsn | None

    CHANNEL_USERNAME: str
    SUPPORT_USERNAME: str
    SUPPORT_USERNAME: str | None = None

    class Config:
        """Configuration for the settings."""

        env_file = ".env"


settings = Settings()
