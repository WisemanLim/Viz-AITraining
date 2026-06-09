"""Settings — env-driven configuration."""
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py → project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _env_file() -> str | None:
    env = os.getenv("ENV", "local")
    path = PROJECT_ROOT / f".env.{env}"
    return str(path) if path.is_file() else None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Viz-AITraining"
    env: str = "local"
    database_url: str = "sqlite:///./local.db"
    redis_url: str = ""
    minio_endpoint: str = ""
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_bucket: str = "viz-artifacts"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"


settings = Settings()
