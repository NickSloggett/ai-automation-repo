"""Application settings and configuration."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field


class APISettings(BaseSettings):
    """API configuration."""

    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    prefix: str = Field(default="/api/v1", env="API_PREFIX")
    cors_origins: List[str] = Field(default=["*"], env="API_CORS_ORIGINS")
    reload: bool = Field(default=False, env="API_RELOAD")
    workers: int = Field(default=1, env="API_WORKERS")

    class Config:
        env_file = ".env"
        case_sensitive = False


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = Field(default="sqlite+aiosqlite:///./ai_automation.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")

    class Config:
        env_file = ".env"
        case_sensitive = False


class RedisSettings(BaseSettings):
    """Redis configuration."""

    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")

    class Config:
        env_file = ".env"
        case_sensitive = False


class CacheSettings(BaseSettings):
    """Caching configuration."""

    enabled: bool = Field(default=True, env="CACHE_ENABLED")
    ttl_default: int = Field(default=3600, env="CACHE_TTL_DEFAULT")
    max_memory_mb: int = Field(default=512, env="CACHE_MAX_MEMORY_MB")
    semantic_threshold: float = Field(default=0.85, env="SEMANTIC_CACHE_THRESHOLD")

    class Config:
        env_file = ".env"
        case_sensitive = False


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    provider: str = Field(default="openai", env="LLM_PROVIDER")
    model: str = Field(default="gpt-4", env="LLM_MODEL")
    api_key: Optional[str] = Field(default=None, env="LLM_API_KEY")
    temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    request_timeout: int = Field(default=60, env="LLM_REQUEST_TIMEOUT")

    # Provider-specific keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


class VectorStoreSettings(BaseSettings):
    """Vector store configuration."""

    provider: str = Field(default="memory", env="VECTOR_STORE_PROVIDER")
    dimension: int = Field(default=1536, env="VECTOR_STORE_DIMENSION")

    # Pinecone
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    pinecone_index: Optional[str] = Field(default=None, env="PINECONE_INDEX")

    # Weaviate
    weaviate_url: Optional[str] = Field(default=None, env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


class MonitoringSettings(BaseSettings):
    """Monitoring and observability configuration."""

    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    tracing_enabled: bool = Field(default=False, env="TRACING_ENABLED")

    class Config:
        env_file = ".env"
        case_sensitive = False


class AuthSettings(BaseSettings):
    """Authentication configuration."""

    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="AUTH_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    class Config:
        env_file = ".env"
        case_sensitive = False


class Settings(BaseSettings):
    """Application settings."""

    # Application
    project_name: str = Field(default="AI Automation Boilerplate", env="PROJECT_NAME")
    version: str = Field(default="0.1.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Nested settings
    api: APISettings = APISettings()
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    cache: CacheSettings = CacheSettings()
    llm: LLMSettings = LLMSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    auth: AuthSettings = AuthSettings()

    # Backward compatibility
    @property
    def enable_caching(self) -> bool:
        return self.cache.enabled

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
