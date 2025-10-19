"""API routes for monitoring and metrics."""

from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..config import get_settings

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])
settings = get_settings()


class MetricsResponse(BaseModel):
    """Schema for metrics response."""

    uptime_seconds: float
    total_requests: int
    active_agents: int
    active_workflows: int
    cache_hit_rate: Optional[float] = None


class HealthCheckResponse(BaseModel):
    """Schema for detailed health check."""

    status: str
    checks: Dict[str, Any]


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get system metrics."""
    try:
        # TODO: Implement actual metrics collection
        # For now, return placeholder data
        return MetricsResponse(
            uptime_seconds=0.0,
            total_requests=0,
            active_agents=0,
            active_workflows=0,
            cache_hit_rate=None,
        )
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}",
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Detailed health check for all services."""
    checks = {}
    overall_status = "healthy"

    # Database check
    try:
        from ..database import engine
        from sqlalchemy import text
        
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "unhealthy"

    # Cache check
    try:
        from ..caching import get_cache_manager
        cache_manager = await get_cache_manager()
        checks["cache"] = {"status": "healthy"}
    except Exception as e:
        checks["cache"] = {"status": "degraded", "error": str(e)}
        if overall_status == "healthy":
            overall_status = "degraded"

    # Vector store check
    try:
        from ..vector_store import get_vector_store
        vector_store = get_vector_store()
        if vector_store.store:
            checks["vector_store"] = {"status": "healthy"}
        else:
            checks["vector_store"] = {"status": "not_configured"}
    except Exception as e:
        checks["vector_store"] = {"status": "degraded", "error": str(e)}

    return HealthCheckResponse(
        status=overall_status,
        checks=checks
    )


@router.get("/config")
async def get_config():
    """Get current configuration (sanitized)."""
    try:
        return {
            "environment": settings.environment,
            "debug": settings.debug,
            "api": {
                "host": settings.api.host,
                "port": settings.api.port,
                "workers": settings.api.workers,
            },
            "database": {
                "driver": settings.database.url.split("://")[0] if "://" in settings.database.url else "unknown",
            },
            "llm": {
                "provider": settings.llm.provider,
                "model": settings.llm.model,
            },
            "vector_store": {
                "provider": settings.vector_store.provider,
                "dimension": settings.vector_store.dimension,
            },
            "cache": {
                "enabled": settings.cache.enabled,
            },
        }
    except Exception as e:
        logger.error("Failed to get config", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config: {str(e)}",
        )

