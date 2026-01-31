from __future__ import annotations 

from functools import lru_cache 
from pathlib import Path 
from typing import Literal 

from pydantic import Field 
from pydantic_settings import BaseSettings , SettingsConfigDict 

# --- Resolve the PATH --- 
BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    """
        Typed Configuration for the API 

        Loads from backend/ .env for local dev 
        but env vars override everthing (Docker/CI friendly)
    """
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR/ ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    # --- App Settings --- 
    app_name: str = "Sanad AI API"
    environment: Literal["local","dev","staging","prod","test"] = "local"
    debug: bool = False
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    # ---- Cors Origins --- 
    cors_origins: list[str] = Field(default_factory=list)
    # --- Database ---
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sanadai"
    # --- MinIO (S3-compatible) ---
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket: str = "sanad-ai"
    # --- AI --- 
    gemini_api_key: str | None = None 
    @property
    def is_production(self) -> bool:
        return self.environment == "prod"
# --- Signature instance With Lru cache ---
@lru_cache
def get_settings() -> Settings:
    return Settings()
