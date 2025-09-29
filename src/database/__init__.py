"""Database connection and session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import get_settings

settings = get_settings()


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    engine = create_async_engine(settings.database.url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
