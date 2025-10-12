"""Application settings and configuration."""

import os
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="AI Automation Boilerplate", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./ai_automation.db", env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Caching
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl_default: int = Field(default=3600, env="CACHE_TTL_DEFAULT")  # 1 hour
    cache_max_memory_mb: int = Field(default=512, env="CACHE_MAX_MEMORY_MB")
    semantic_cache_threshold: float = Field(default=0.85, env="SEMANTIC_CACHE_THRESHOLD")

    # Secrets management
    secrets_provider: str = Field(default="auto", env="SECRETS_PROVIDER")  # auto, vault, aws, env
    vault_url: Optional[str] = Field(default=None, env="VAULT_URL")
    vault_token: Optional[str] = Field(default=None, env="VAULT_TOKEN")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")

    # Authentication
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # LLM Providers
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")

    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
