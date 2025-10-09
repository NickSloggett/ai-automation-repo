"""Workflow models and data structures."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepCondition(BaseModel):
    """Condition for conditional step execution."""

    type: str = Field(..., description="Condition type: 'equals', 'contains', 'greater_than', etc.")
    field: str = Field(..., description="Field to check from previous step output")
    value: Any = Field(..., description="Value to compare against")
    operator: str = Field(default="equals", description="Comparison operator")


class WorkflowStep(BaseModel):
    """Workflow step definition."""

    id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Step name")
    agent_type: str = Field(..., description="Agent type to execute")
    agent_config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Step inputs")
    depends_on: List[str] = Field(default_factory=list, description="Step dependencies")
    condition: Optional[StepCondition] = Field(None, description="Conditional execution")
    retry_on_failure: bool = Field(default=True, description="Retry on failure")
    timeout: int = Field(default=300, description="Step timeout in seconds")
    parallel: bool = Field(default=False, description="Can run in parallel")


class StepResult(BaseModel):
    """Result from a workflow step execution."""

    step_id: str
    status: WorkflowStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowConfig(BaseModel):
    """Workflow configuration."""

    name: str = Field(..., description="Workflow name")
    description: str = Field(default="", description="Workflow description")
    version: str = Field(default="1.0.0", description="Workflow version")
    max_retries: int = Field(default=3, description="Maximum retries per step")
    timeout: int = Field(default=3600, description="Total workflow timeout")
    parallel_execution: bool = Field(default=False, description="Enable parallel execution")
    on_failure: str = Field(default="stop", description="Failure handling: 'stop', 'continue', 'rollback'")
    save_intermediate: bool = Field(default=True, description="Save intermediate results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Workflow(BaseModel):
    """Complete workflow definition."""

    id: str = Field(..., description="Unique workflow identifier")
    config: WorkflowConfig
    steps: List[WorkflowStep]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowResult(BaseModel):
    """Result from workflow execution."""

    workflow_id: str
    status: WorkflowStatus
    step_results: Dict[str, StepResult] = Field(default_factory=dict)
    final_output: Optional[Any] = None
    error: Optional[str] = None
    total_execution_time: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionContext(BaseModel):
    """Context maintained during workflow execution."""

    workflow_id: str
    current_step: Optional[str] = None
    completed_steps: List[str] = Field(default_factory=list)
    step_outputs: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=datetime.utcnow)





