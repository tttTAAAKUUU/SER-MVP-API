"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Database
    database_url: str = "sqlite+aiosqlite:///./sir_dev.db"
    sqlalchemy_echo: bool = False

    # JWT
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # App
    app_name: str = "SIR"
    debug: bool = False
    api_version: str = "v1"

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    # Admin
    admin_email: str = "admin@sir.local"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
