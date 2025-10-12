"""FastAPI application for AI Automation Boilerplate."""

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .logging import setup_logging, get_logger
from .monitoring import init_monitoring

# Setup logging and monitoring
setup_logging()
init_monitoring()

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AI Automation Boilerplate API",
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.project_name}",
        "version": settings.version,
        "environment": settings.environment,
        "docs_url": "/docs",
    }

@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe with database connectivity check."""
    try:
        # Check database connectivity
        from .database import get_db
        db = get_db()
        await db.execute("SELECT 1")  # Simple connectivity test

        # Check vector store if configured
        from .config import get_settings
        settings = get_settings()
        if settings.vector_store.provider != "memory":
            from .vector_store import get_vector_store
            vector_store = get_vector_store()
            # Quick health check for vector store
            await vector_store.health_check()

        return {
            "status": "ready",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "database": "healthy",
                "vector_store": "healthy" if settings.vector_store.provider != "memory" else "n/a"
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not ready",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe with basic system health."""
    import psutil
    import os

    try:
        # Basic system health checks
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)

        # Check if critical services are running
        critical_services_healthy = True

        # Memory usage check (alert if > 90%)
        if memory_percent > 90:
            critical_services_healthy = False

        # CPU usage check (alert if > 95%)
        if cpu_percent > 95:
            critical_services_healthy = False

        return {
            "status": "alive" if critical_services_healthy else "degraded",
            "timestamp": "2024-01-01T00:00:00Z",
            "system": {
                "memory_usage_percent": memory_percent,
                "cpu_usage_percent": cpu_percent,
                "uptime_seconds": int(time.time() - psutil.boot_time())
            }
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.get("/info")
async def app_info():
    """Application information."""
    from .circuit_breaker import get_circuit_breaker_stats
    from .caching import get_cache_manager

    circuit_breaker_stats = await get_circuit_breaker_stats()
    cache_manager = await get_cache_manager()
    cache_stats = await cache_manager.get_stats()

    return {
        "name": settings.project_name,
        "version": settings.version,
        "environment": settings.environment,
        "debug": settings.debug,
        "database_url": settings.database.url.replace(settings.database.url.split("://")[1].split("@")[0], "***") if "://" in settings.database.url else "***",
        "vector_store": settings.vector_store.provider,
        "llm_provider": settings.llm.provider,
        "circuit_breakers": circuit_breaker_stats,
        "cache_stats": cache_stats,
    }

# Import and include routers
from .routers import agents_router

# Include routers
app.include_router(agents_router)

# Cost tracking endpoints
@app.get("/costs/summary")
async def get_cost_summary(
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    agent_name: Optional[str] = None,
):
    """Get cost summary."""
    from .cost_tracking import get_cost_tracker

    tracker = await get_cost_tracker()
    summary = await tracker.get_cost_summary(
        start_time=start_time,
        end_time=end_time,
        agent_name=agent_name
    )
    return summary.dict()

@app.get("/costs/alerts")
async def get_cost_alerts(since: Optional[float] = None):
    """Get cost alerts."""
    from .cost_tracking import get_cost_tracker

    tracker = await get_cost_tracker()
    alerts = await tracker.get_alerts(since=since)
    return [alert.dict() for alert in alerts]

@app.post("/costs/budget")
async def set_budget_limit(category: str, limit: float):
    """Set budget limit."""
    from .cost_tracking import get_cost_tracker

    tracker = await get_cost_tracker()
    await tracker.set_budget_limit(category, limit)
    return {"message": f"Budget limit set for {category}: ${limit}"}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    from .database import init_db
    from .caching import get_cache_manager
    from .cost_tracking import get_cost_tracker
    from .secrets import get_secrets_manager

    await init_db()

    # Initialize secrets manager
    secrets_manager = await get_secrets_manager()
    logger.info("Secrets manager initialized")

    # Initialize cache manager
    cache_manager = await get_cache_manager()
    logger.info("Cache manager initialized")

    # Initialize cost tracker
    cost_tracker = await get_cost_tracker()
    logger.info("Cost tracker initialized")

    logger.info("Application started", environment=settings.environment)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    from .database import close_db
    from .caching import close_cache_manager

    await close_db()
    await close_cache_manager()
    logger.info("Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        workers=settings.api.workers,
    )
