"""FastAPI application for AI Automation Boilerplate."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .logging import setup_logging
from .monitoring import init_monitoring

# Setup logging and monitoring
setup_logging()
init_monitoring()

# Get settings
settings = get_settings()

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
    """Kubernetes readiness probe."""
    return {"status": "ready"}

@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

@app.get("/info")
async def app_info():
    """Application information."""
    return {
        "name": settings.project_name,
        "version": settings.version,
        "environment": settings.environment,
        "debug": settings.debug,
        "database_url": settings.database.url.replace(settings.database.url.split("://")[1].split("@")[0], "***") if "://" in settings.database.url else "***",
        "vector_store": settings.vector_store.provider,
        "llm_provider": settings.llm.provider,
    }

# Import and include routers
# from .routers import agents, workflows, monitoring

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        workers=settings.api.workers,
    )
