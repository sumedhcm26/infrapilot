"""
Configuration Management
========================
Pydantic BaseSettings reads values from environment variables automatically.
If a value isn't found in the environment, it falls back to the default.

This is the standard pattern for 12-Factor App configuration:
https://12factor.net/config

Usage: from app.config import settings
Then access: settings.DATABASE_URL, settings.SECRET_KEY, etc.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    All application settings are defined here as class attributes.
    Pydantic will automatically read from environment variables
    (case-insensitive) or from a .env file.
    """

    # App Info
    APP_NAME: str = "InfraPilot"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # Database
    # SQLite is used for local dev - no installation needed!
    # For production, switch to: postgresql+asyncpg://user:pass@host/dbname
    DATABASE_URL: str = "sqlite+aiosqlite:///./infrapilot.db"

    # Security
    SECRET_KEY: str = "change-this-in-production-use-openssl-rand-hex-32"

    # CORS - which frontend origins are allowed to call this API
    # In production: ["https://your-frontend.vercel.app"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
    ]

    # Health Check Settings
    HEALTH_CHECK_INTERVAL: int = 60    # seconds between each check cycle
    HEALTH_CHECK_TIMEOUT: int = 10     # seconds before a request times out

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        # Load from .env file if it exists
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create a single shared instance
# Import this instance everywhere: from app.config import settings
settings = Settings()
