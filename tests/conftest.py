"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.api import app
from src.database import Base, get_db
from src.config import get_settings

settings = get_settings()

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Create test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """Create a test client with database override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "content": "This is a test response from the LLM.",
        "model": "test-model",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
        "finish_reason": "stop",
    }


@pytest.fixture
def sample_agent_config():
    """Sample agent configuration for testing."""
    return {
        "name": "test_agent",
        "description": "Test agent",
        "max_retries": 3,
        "timeout": 300,
        "enable_caching": True,
        "cache_ttl": 3600,
    }


@pytest.fixture
def sample_task_config():
    """Sample task configuration for testing."""
    return {
        "name": "test_task_agent",
        "description": "Test task agent",
        "task_type": "email_processing",
        "required_tools": ["email_reader", "categorizer"],
        "output_format": "json",
        "validate_output": True,
        "max_retries": 3,
        "timeout": 300,
    }


@pytest.fixture
def sample_decision_config():
    """Sample decision configuration for testing."""
    return {
        "name": "test_decision_agent",
        "description": "Test decision agent",
        "decision_criteria": ["urgency", "impact", "resources"],
        "confidence_threshold": 0.8,
        "alternatives": ["option_a", "option_b", "option_c"],
        "reasoning_steps": 3,
        "max_retries": 3,
        "timeout": 300,
    }







