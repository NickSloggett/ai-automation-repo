"""Tests for database models and operations."""

import pytest
from datetime import datetime
from sqlalchemy import select

from src.database.models import (
    Agent,
    AgentExecution,
    AgentStatus,
    Workflow,
    WorkflowExecution,
    WorkflowStatus,
    User,
)


@pytest.mark.asyncio
async def test_create_agent(db_session):
    """Test creating an agent in the database."""
    agent = Agent(
        name="test_agent",
        description="Test agent description",
        agent_type="task",
        config={"max_retries": 3},
    )

    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)

    assert agent.id is not None
    assert agent.name == "test_agent"
    assert agent.is_active is True
    assert agent.created_at is not None


@pytest.mark.asyncio
async def test_create_agent_execution(db_session):
    """Test creating an agent execution."""
    # Create agent first
    agent = Agent(
        name="test_agent",
        description="Test agent",
        agent_type="task",
        config={},
    )
    db_session.add(agent)
    await db_session.commit()

    # Create execution
    execution = AgentExecution(
        agent_id=agent.id,
        status=AgentStatus.PENDING,
        input_data={"test": "data"},
    )
    db_session.add(execution)
    await db_session.commit()
    await db_session.refresh(execution)

    assert execution.id is not None
    assert execution.agent_id == agent.id
    assert execution.status == AgentStatus.PENDING
    assert execution.started_at is not None


@pytest.mark.asyncio
async def test_agent_execution_relationship(db_session):
    """Test agent-execution relationship."""
    agent = Agent(
        name="test_agent",
        description="Test agent",
        agent_type="task",
        config={},
    )
    db_session.add(agent)
    await db_session.commit()

    # Create multiple executions
    for i in range(3):
        execution = AgentExecution(
            agent_id=agent.id,
            status=AgentStatus.SUCCESS,
            input_data={"iteration": i},
            output_data={"result": i * 2},
        )
        db_session.add(execution)

    await db_session.commit()

    # Query agent with executions
    result = await db_session.execute(select(Agent).where(Agent.id == agent.id))
    agent_with_execs = result.scalar_one()

    assert len(agent_with_execs.executions) == 3


@pytest.mark.asyncio
async def test_create_workflow(db_session):
    """Test creating a workflow."""
    workflow = Workflow(
        name="test_workflow",
        description="Test workflow",
        steps=[
            {"name": "step1", "action": "process"},
            {"name": "step2", "action": "validate"},
        ],
        config={"timeout": 300},
    )

    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)

    assert workflow.id is not None
    assert workflow.name == "test_workflow"
    assert len(workflow.steps) == 2
    assert workflow.is_active is True


@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_here",
        is_active=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_superuser is False


@pytest.mark.asyncio
async def test_user_api_requests_relationship(db_session):
    """Test user-api_requests relationship."""
    from src.database.models import APIRequest

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed",
    )
    db_session.add(user)
    await db_session.commit()

    # Create API requests
    for i in range(2):
        request = APIRequest(
            user_id=user.id,
            endpoint=f"/api/test/{i}",
            method="GET",
            status_code=200,
            response_time=0.1,
        )
        db_session.add(request)

    await db_session.commit()

    # Query user with requests
    result = await db_session.execute(select(User).where(User.id == user.id))
    user_with_reqs = result.scalar_one()

    assert len(user_with_reqs.api_requests) == 2







