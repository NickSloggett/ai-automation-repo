"""API routes for workflow management and execution."""

from typing import List, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..database.models import Workflow, WorkflowExecution, WorkflowStatus as DBWorkflowStatus
from ..workflows.engine import WorkflowEngine
from ..workflows.models import Workflow as WorkflowModel, WorkflowConfig, WorkflowStep

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/workflows", tags=["workflows"])


class WorkflowCreate(BaseModel):
    """Schema for creating a workflow."""

    name: str
    description: Optional[str] = None
    steps: List[dict]
    config: dict = {}


class WorkflowResponse(BaseModel):
    """Schema for workflow response."""

    id: str
    name: str
    description: Optional[str]
    steps: List[dict]
    config: dict
    is_active: bool

    class Config:
        from_attributes = True


class WorkflowExecuteRequest(BaseModel):
    """Schema for workflow execution request."""

    input_data: dict = {}


class WorkflowExecutionResponse(BaseModel):
    """Schema for workflow execution response."""

    id: str
    workflow_id: str
    status: str
    input_data: dict
    output_data: Optional[dict]
    error: Optional[str]
    current_step: int
    total_steps: int

    class Config:
        from_attributes = True


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(workflow: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    """Create a new workflow."""
    try:
        db_workflow = Workflow(
            name=workflow.name,
            description=workflow.description,
            steps=workflow.steps,
            config=workflow.config,
        )
        db.add(db_workflow)
        await db.commit()
        await db.refresh(db_workflow)

        logger.info("Workflow created", workflow_id=db_workflow.id, workflow_name=db_workflow.name)
        return db_workflow

    except Exception as e:
        logger.error("Failed to create workflow", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}",
        )


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all workflows."""
    try:
        query = select(Workflow)
        if is_active is not None:
            query = query.where(Workflow.is_active == is_active)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        workflows = result.scalars().all()

        return workflows

    except Exception as e:
        logger.error("Failed to list workflows", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}",
        )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific workflow by ID."""
    try:
        result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found",
            )

        return workflow

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get workflow", workflow_id=workflow_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}",
        )


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    request: WorkflowExecuteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a workflow."""
    try:
        # Get workflow from database
        result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found",
            )

        if not workflow.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workflow {workflow_id} is not active",
            )

        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=DBWorkflowStatus.RUNNING,
            input_data=request.input_data,
            total_steps=len(workflow.steps),
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        # TODO: Execute workflow asynchronously
        # For now, just mark as pending
        logger.info(
            "Workflow execution created",
            workflow_id=workflow_id,
            execution_id=execution.id
        )

        return execution

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute workflow", workflow_id=workflow_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}",
        )


@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(
    workflow_id: str,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List executions for a workflow."""
    try:
        query = select(WorkflowExecution).where(WorkflowExecution.workflow_id == workflow_id)

        if status_filter:
            query = query.where(WorkflowExecution.status == status_filter)

        query = query.order_by(WorkflowExecution.started_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        executions = result.scalars().all()

        return executions

    except Exception as e:
        logger.error("Failed to list workflow executions", workflow_id=workflow_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflow executions: {str(e)}",
        )


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a workflow."""
    try:
        result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found",
            )

        await db.delete(workflow)
        await db.commit()

        logger.info("Workflow deleted", workflow_id=workflow_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete workflow", workflow_id=workflow_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workflow: {str(e)}",
        )

