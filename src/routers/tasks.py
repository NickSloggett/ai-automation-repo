"""API routes for background task management."""

from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..database.models import Task, AgentStatus

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    """Schema for creating a task."""

    task_type: str
    payload: dict
    priority: int = 0
    max_retries: int = 3


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: str
    task_type: str
    status: str
    payload: dict
    result: Optional[dict]
    error: Optional[str]
    priority: int
    retries: int
    max_retries: int

    class Config:
        from_attributes = True


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new background task."""
    try:
        db_task = Task(
            task_type=task.task_type,
            payload=task.payload,
            priority=task.priority,
            max_retries=task.max_retries,
            status=AgentStatus.PENDING,
        )
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)

        logger.info("Task created", task_id=db_task.id, task_type=db_task.task_type)
        return db_task

    except Exception as e:
        logger.error("Failed to create task", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}",
        )


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    task_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all tasks."""
    try:
        query = select(Task)
        
        if status_filter:
            query = query.where(Task.status == status_filter)
        
        if task_type:
            query = query.where(Task.task_type == task_type)

        query = query.order_by(Task.priority.desc(), Task.scheduled_at.asc()).offset(skip).limit(limit)
        result = await db.execute(query)
        tasks = result.scalars().all()

        return tasks

    except Exception as e:
        logger.error("Failed to list tasks", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}",
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific task by ID."""
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get task", task_id=task_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}",
        )


@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Retry a failed task."""
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )

        if task.status not in [AgentStatus.FAILED, AgentStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task {task_id} is not in a retriable state",
            )

        # Reset task for retry
        task.status = AgentStatus.PENDING
        task.error = None
        task.started_at = None
        task.completed_at = None
        
        await db.commit()
        await db.refresh(task)

        logger.info("Task retry requested", task_id=task_id)
        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retry task", task_id=task_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry task: {str(e)}",
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a task."""
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )

        await db.delete(task)
        await db.commit()

        logger.info("Task deleted", task_id=task_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete task", task_id=task_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}",
        )

