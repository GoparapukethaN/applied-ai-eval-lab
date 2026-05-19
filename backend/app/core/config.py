from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Applied AI Eval Lab"
    environment: Literal["local", "test", "production"] = "local"
    frontend_origin: str = "http://localhost:3000"
    max_upload_chars: int = Field(default=80_000, ge=1_000, le=500_000)
    default_chunk_size: int = Field(default=900, ge=300, le=2_000)
    default_chunk_overlap: int = Field(default=120, ge=0, le=500)
    retrieval_top_k: int = Field(default=4, ge=1, le=12)

    model_config = SettingsConfigDict(
        env_prefix="AIEL_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

