from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for AuditAgent."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_ignore_empty=True,
    )

    # Application
    app_name: str = "AuditAgent"
    app_environment: Literal["development", "testing", "production"] = (
        "development"
    )

    # LLM
    groq_api_key: SecretStr | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    llm_timeout_seconds: float = Field(default=30.0, gt=0, le=300)

    # Web search
    tavily_api_key: SecretStr | None = None
    web_fallback_enabled: bool = True

    # Document processing
    chunk_size: int = Field(default=1000, ge=100, le=10000)
    chunk_overlap: int = Field(default=200, ge=0)

    # Retrieval
    top_k: int = Field(default=4, ge=1, le=100)
    rrf_k: int = Field(default=60, ge=1)
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Agent workflow
    max_retry_count: int = Field(default=2, ge=0, le=2)

    @model_validator(mode="after")
    def validate_chunk_overlap(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached application configuration."""

    return Settings()