"""Configuration management for AI automation boilerplate."""

import os
from typing import Optional

from pydantic import BaseSettings, Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    url: str = Field(default="sqlite:///./ai_automation.db", env="DATABASE_URL")
    pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")

    class Config:
        env_prefix = "DB_"


class VectorStoreSettings(BaseSettings):
    """Vector store configuration settings."""

    provider: str = Field(default="pinecone", env="VECTOR_STORE_PROVIDER")
    api_key: Optional[str] = Field(default=None, env="VECTOR_STORE_API_KEY")
    index_name: str = Field(default="ai-automation-index", env="VECTOR_STORE_INDEX_NAME")
    dimension: int = Field(default=1536, env="VECTOR_STORE_DIMENSION")
    metric: str = Field(default="cosine", env="VECTOR_STORE_METRIC")

    class Config:
        env_prefix = "VECTOR_"


class LLMSettings(BaseSettings):
    """Large Language Model configuration settings."""

    provider: str = Field(default="openai", env="LLM_PROVIDER")
    model: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL")
    api_key: Optional[str] = Field(default=None, env="LLM_API_KEY")
    temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2048, env="LLM_MAX_TOKENS")
    request_timeout: int = Field(default=60, env="LLM_REQUEST_TIMEOUT")

    class Config:
        env_prefix = "LLM_"


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration settings."""

    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

    class Config:
        env_prefix = "MONITORING_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    auth0_domain: Optional[str] = Field(default=None, env="AUTH0_DOMAIN")
    auth0_client_id: Optional[str] = Field(default=None, env="AUTH0_CLIENT_ID")
    auth0_client_secret: Optional[str] = Field(default=None, env="AUTH0_CLIENT_SECRET")

    class Config:
        env_prefix = "SECURITY_"


class APISettings(BaseSettings):
    """API configuration settings."""

    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=False, env="API_RELOAD")
    cors_origins: list[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")

    class Config:
        env_prefix = "API_"


class AutomationSettings(BaseSettings):
    """Automation-specific configuration settings."""

    max_concurrent_tasks: int = Field(default=10, env="MAX_CONCURRENT_TASKS")
    task_timeout: int = Field(default=300, env="TASK_TIMEOUT")
    retry_attempts: int = Field(default=3, env="RETRY_ATTEMPTS")
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")

    class Config:
        env_prefix = "AUTOMATION_"


class Settings(BaseSettings):
    """Main application settings."""

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Core settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    api: APISettings = Field(default_factory=APISettings)
    automation: AutomationSettings = Field(default_factory=AutomationSettings)

    # Project settings
    project_name: str = Field(default="AI Automation Boilerplate", env="PROJECT_NAME")
    version: str = Field(default="0.1.0", env="PROJECT_VERSION")

    @validator("environment")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the current application settings."""
    return settings


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.environment == "production"


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.environment == "development"
