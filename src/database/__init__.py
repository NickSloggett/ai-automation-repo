"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from ..config import get_settings

settings = get_settings()

# Create base class for declarative models
Base = declarative_base()

# Convert sync URL to async URL
database_url = settings.database.url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
elif database_url.startswith("sqlite://"):
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")

# Create async engine
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=settings.database.pool_size if "sqlite" not in database_url else 0,
    max_overflow=settings.database.max_overflow if "sqlite" not in database_url else 0,
    pool_timeout=settings.database.pool_timeout,
    poolclass=NullPool if "sqlite" in database_url else None,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


__all__ = ["Base", "get_db", "init_db", "close_db", "AsyncSessionLocal", "engine"]