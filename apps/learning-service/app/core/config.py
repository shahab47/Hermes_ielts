"""Application configuration via environment variables."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = {"env_prefix": "IELTS_", "env_file": ".env", "extra": "ignore"}

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://ielts:ielts_dev@localhost:5432/ielts_learning",
        description="PostgreSQL connection string",
    )

    # Application
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or console")

    # Security
    admin_api_key: str = Field(default="", description="Admin API key for internal endpoints")


settings = Settings()
