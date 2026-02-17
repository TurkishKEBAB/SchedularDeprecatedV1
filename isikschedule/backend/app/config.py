"""
Application configuration using pydantic-settings.
"""

import sys
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application
    APP_NAME: str = "IşıkSchedule"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/isikschedule"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Job Settings
    JOB_TIMEOUT_SECONDS: int = 300
    MAX_SCHEDULES_PER_JOB: int = 50
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    
    # Validate SECRET_KEY on startup (fail-fast)
    weak_keys = [
        "change-me-in-production",
        "your-secret-key-change-in-production",
        "your-strong-random-secret-key-at-least-32-characters-long",
        "secret",
        "changeme",
        "test",
    ]
    
    if settings.SECRET_KEY in weak_keys or len(settings.SECRET_KEY) < 32:
        print(f"❌ CRITICAL: SECRET_KEY is too weak or using default value!")
        print("   SECRET_KEY must be at least 32 characters long and unique.")
        print("   Generate a strong key with: openssl rand -hex 32")
        sys.exit(1)
    
    return settings


settings = get_settings()
