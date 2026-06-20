"""
Application configuration.

Loads settings from environment variables (with sane local-dev defaults)
using pydantic-settings so the rest of the app never touches os.environ
directly.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = "CHANGE_ME_TO_A_RANDOM_SECRET_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "sqlite:///./job_tracker.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
