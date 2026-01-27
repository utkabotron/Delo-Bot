from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Ensure data directory exists
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database path with proper URL format
DB_PATH = DATA_DIR / "deloculator.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


class Settings(BaseSettings):
    telegram_bot_token: str = ""
    google_sheets_id: str = "18vDpWaCYA1rFhsyb54JhXXtR2b7RVsRplpiWZ93g1N8"
    google_credentials_file: str = "credentials.json"
    database_url: str = DATABASE_URL
    cors_origins: str = "http://localhost:8000,http://localhost:5500,http://127.0.0.1:8000"
    app_password: str = "deloculator2024"
    csrf_secret: str = "change-this-secret-in-production"  # Secret for signing CSRF tokens
    environment: str = "development"  # development, staging, production

    class Config:
        env_file = ".env"

    def validate_production_settings(self) -> list[str]:
        """
        Validate that production-critical settings are properly configured.

        Returns:
            List of validation warnings (empty if all good)
        """
        warnings = []

        # Check if default password is used in production
        if self.environment == "production" and self.app_password == "deloculator2024":
            warnings.append("WARNING: Using default APP_PASSWORD in production! Change it immediately.")

        # Check if default CSRF secret is used
        if self.csrf_secret == "change-this-secret-in-production":
            warnings.append("WARNING: Using default CSRF_SECRET! Generate a random secret.")

        # Check if credentials file exists
        creds_path = PROJECT_ROOT / self.google_credentials_file
        if not creds_path.exists():
            warnings.append(f"WARNING: Google credentials file not found: {creds_path}")

        return warnings


@lru_cache()
def get_settings() -> Settings:
    return Settings()
