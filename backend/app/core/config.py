"""
FraudShield Core Configuration.
Loads and validates application settings using Pydantic Settings.
"""

from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Information
    APP_NAME: str = "FraudShield"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FraudShield AI Fraud Detection Platform"
    VERSION: str = "1.0.0"

    # Security & Tokens
    SECRET_KEY: str = "fraudshield-super-secret-development-key-change-in-production-1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "fraudshield_user"
    POSTGRES_PASSWORD: str = "fraudshield_secret_password"
    POSTGRES_DB: str = "fraudshield_db"

    # Default to SQLite for local development / testing if Postgres is not spun up
    # Supports PostgreSQL URL when environment variables are set
    DATABASE_URL: str = "sqlite+aiosqlite:///./fraudshield.db"
    SYNC_DATABASE_URL: str = "sqlite:///./fraudshield.db"

    # Redis & Background Workers
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Machine Learning Artifacts
    ARTIFACTS_DIR: Path = Path("ml/artifacts")
    CHAMPION_MODEL_VERSION: str = "v1.0.0"

    # Seed Admin User
    FIRST_SUPERUSER_EMAIL: str = "admin@fraudshield.io"
    FIRST_SUPERUSER_PASSWORD: str = "AdminPassword123!"
    FIRST_SUPERUSER_NAME: str = "System Administrator"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://fraud-shield-one-khaki.vercel.app",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Risk Engine Default Thresholds
    RISK_THRESHOLD_LOW: float = 0.30
    RISK_THRESHOLD_HIGH: float = 0.70
    VELOCITY_TIME_WINDOW_HOURS: int = 24
    VELOCITY_TXN_COUNT_THRESHOLD: int = 5
    AMOUNT_SPIKE_MULTIPLIER: float = 3.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
