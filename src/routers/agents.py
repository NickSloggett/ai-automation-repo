"""API routes for agent management and execution."""

from typing import List, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..database.models import Agent, AgentExecution, AgentStatus as DBAgentStatus
from ..agents.base import AgentConfig, AgentResult
from ..agents.task import TaskAgent, TaskConfig
from ..agents.decision import DecisionAgent, DecisionConfig

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


class AgentCreate(BaseModel):
    """Schema for creating an agent."""

    name: str
    description: Optional[str] = None
    agent_type: str
    config: dict


class AgentResponse(BaseModel):
    """Schema for agent response."""

    id: str
    name: str
    description: Optional[str]
    agent_type: str
    config: dict
    is_active: bool

    class Config:
        from_attributes = True


class AgentExecuteRequest(BaseModel):
    """Schema for agent execution request."""

    input_data: dict


class AgentExecutionResponse(BaseModel):
    """Schema for agent execution response."""

    id: str
    agent_id: str
    status: str
    input_data: dict
    output_data: Optional[dict]
    error: Optional[str]
    execution_time: Optional[float]

    class Config:
        from_attributes = True


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new agent."""
    try:
        db_agent = Agent(
            name=agent.name,
            description=agent.description,
            agent_type=agent.agent_type,
            config=agent.config,
        )
        db.add(db_agent)
        await db.commit()
        await db.refresh(db_agent)

        logger.info("Agent created", agent_id=db_agent.id, agent_name=db_agent.name)
        return db_agent

    except Exception as e:
        logger.error("Failed to create agent", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}",
        )


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all agents."""
    try:
        query = select(Agent)
        if is_active is not None:
            query = query.where(Agent.is_active == is_active)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        agents = result.scalars().all()

        return agents

    except Exception as e:
        logger.error("Failed to list agents", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}",
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific agent by ID."""
    try:
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )

        return agent

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent", agent_id=agent_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}",
        )


@router.post("/{agent_id}/execute", response_model=AgentExecutionResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute an agent."""
    try:
        # Get agent from database
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )

        if not agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent {agent_id} is not active",
            )

        # Create execution record
        execution = AgentExecution(
            agent_id=agent_id,
            status=DBAgentStatus.RUNNING,
            input_data=request.input_data,
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        # Execute agent based on type
        try:
            if agent.agent_type == "task":
                config = TaskConfig(**agent.config)
                agent_instance = TaskAgent(config)
            elif agent.agent_type == "decision":
                config = DecisionConfig(**agent.config)
                agent_instance = DecisionAgent(config)
            else:
                raise ValueError(f"Unknown agent type: {agent.agent_type}")

            # Run agent
            result = await agent_instance.execute_with_retry(request.input_data)

            # Update execution record
            execution.status = DBAgentStatus.SUCCESS if result.success else DBAgentStatus.FAILED
            execution.output_data = result.data
            execution.error = result.error
            execution.execution_time = result.execution_time
            execution.metadata = result.metadata

        except Exception as e:
            execution.status = DBAgentStatus.FAILED
            execution.error = str(e)
            logger.error("Agent execution failed", agent_id=agent_id, error=str(e), exc_info=True)

        finally:
            await db.commit()
            await db.refresh(execution)

        return execution

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute agent", agent_id=agent_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute agent: {str(e)}",
        )


@router.get("/{agent_id}/executions", response_model=List[AgentExecutionResponse])
async def list_agent_executions(
    agent_id: str,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List executions for an agent."""
    try:
        query = select(AgentExecution).where(AgentExecution.agent_id == agent_id)

        if status_filter:
            query = query.where(AgentExecution.status == status_filter)

        query = query.order_by(AgentExecution.started_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        executions = result.scalars().all()

        return executions

    except Exception as e:
        logger.error("Failed to list agent executions", agent_id=agent_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agent executions: {str(e)}",
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an agent."""
    try:
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )

        await db.delete(agent)
        await db.commit()

        logger.info("Agent deleted", agent_id=agent_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete agent", agent_id=agent_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}",
        )
