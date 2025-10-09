"""Fluent workflow builder for easy workflow construction."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from .models import (
    Workflow,
    WorkflowStep,
    WorkflowConfig,
    StepCondition,
)


class WorkflowBuilder:
    """Fluent builder for workflows."""

    def __init__(self, name: str, description: str = ""):
        """Initialize workflow builder.

        Args:
            name: Workflow name
            description: Workflow description
        """
        self.workflow_id = str(uuid.uuid4())
        self.config = WorkflowConfig(name=name, description=description)
        self.steps: List[WorkflowStep] = []
        self._last_step_id: Optional[str] = None

    def with_config(
        self,
        max_retries: int = None,
        timeout: int = None,
        parallel_execution: bool = None,
        on_failure: str = None,
    ) -> "WorkflowBuilder":
        """Configure workflow settings.

        Args:
            max_retries: Maximum retries per step
            timeout: Total workflow timeout
            parallel_execution: Enable parallel execution
            on_failure: Failure handling strategy

        Returns:
            Self for chaining
        """
        if max_retries is not None:
            self.config.max_retries = max_retries
        if timeout is not None:
            self.config.timeout = timeout
        if parallel_execution is not None:
            self.config.parallel_execution = parallel_execution
        if on_failure is not None:
            self.config.on_failure = on_failure

        return self

    def add_step(
        self,
        name: str,
        agent_type: str,
        agent_config: Dict[str, Any] = None,
        inputs: Dict[str, Any] = None,
        depends_on: List[str] = None,
        timeout: int = 300,
        step_id: str = None,
    ) -> "WorkflowBuilder":
        """Add a step to the workflow.

        Args:
            name: Step name
            agent_type: Type of agent to use
            agent_config: Agent configuration
            inputs: Step inputs
            depends_on: List of step IDs this step depends on
            timeout: Step timeout in seconds
            step_id: Optional custom step ID

        Returns:
            Self for chaining
        """
        if step_id is None:
            step_id = f"step_{len(self.steps) + 1}"

        step = WorkflowStep(
            id=step_id,
            name=name,
            agent_type=agent_type,
            agent_config=agent_config or {},
            inputs=inputs or {},
            depends_on=depends_on or [],
            timeout=timeout,
        )

        self.steps.append(step)
        self._last_step_id = step_id

        return self

    def add_task_step(
        self,
        name: str,
        task_type: str,
        inputs: Dict[str, Any] = None,
        required_tools: List[str] = None,
        depends_on: List[str] = None,
        timeout: int = 300,
    ) -> "WorkflowBuilder":
        """Add a task agent step.

        Args:
            name: Step name
            task_type: Type of task
            inputs: Step inputs
            required_tools: Required tools
            depends_on: Dependencies
            timeout: Timeout in seconds

        Returns:
            Self for chaining
        """
        agent_config = {
            "name": name,
            "description": f"Task: {task_type}",
            "task_type": task_type,
            "required_tools": required_tools or [],
        }

        return self.add_step(
            name=name,
            agent_type="task",
            agent_config=agent_config,
            inputs=inputs,
            depends_on=depends_on,
            timeout=timeout,
        )

    def add_decision_step(
        self,
        name: str,
        decision_criteria: List[str],
        alternatives: List[str],
        inputs: Dict[str, Any] = None,
        confidence_threshold: float = 0.8,
        depends_on: List[str] = None,
        timeout: int = 300,
    ) -> "WorkflowBuilder":
        """Add a decision agent step.

        Args:
            name: Step name
            decision_criteria: Decision criteria
            alternatives: Decision alternatives
            inputs: Step inputs
            confidence_threshold: Confidence threshold
            depends_on: Dependencies
            timeout: Timeout in seconds

        Returns:
            Self for chaining
        """
        agent_config = {
            "name": name,
            "description": f"Decision: {name}",
            "decision_criteria": decision_criteria,
            "alternatives": alternatives,
            "confidence_threshold": confidence_threshold,
        }

        return self.add_step(
            name=name,
            agent_type="decision",
            agent_config=agent_config,
            inputs=inputs,
            depends_on=depends_on,
            timeout=timeout,
        )

    def add_conditional_step(
        self,
        name: str,
        agent_type: str,
        condition_field: str,
        condition_value: Any,
        condition_operator: str = "equals",
        agent_config: Dict[str, Any] = None,
        inputs: Dict[str, Any] = None,
        depends_on: List[str] = None,
    ) -> "WorkflowBuilder":
        """Add a conditional step.

        Args:
            name: Step name
            agent_type: Type of agent
            condition_field: Field to check
            condition_value: Value to compare
            condition_operator: Comparison operator
            agent_config: Agent configuration
            inputs: Step inputs
            depends_on: Dependencies

        Returns:
            Self for chaining
        """
        step_id = f"step_{len(self.steps) + 1}"

        condition = StepCondition(
            type="simple",
            field=condition_field,
            value=condition_value,
            operator=condition_operator,
        )

        step = WorkflowStep(
            id=step_id,
            name=name,
            agent_type=agent_type,
            agent_config=agent_config or {},
            inputs=inputs or {},
            depends_on=depends_on or [],
            condition=condition,
        )

        self.steps.append(step)
        self._last_step_id = step_id

        return self

    def then(
        self,
        name: str,
        agent_type: str,
        agent_config: Dict[str, Any] = None,
        inputs: Dict[str, Any] = None,
        timeout: int = 300,
    ) -> "WorkflowBuilder":
        """Add a step that depends on the previous step.

        Args:
            name: Step name
            agent_type: Type of agent
            agent_config: Agent configuration
            inputs: Step inputs
            timeout: Timeout in seconds

        Returns:
            Self for chaining
        """
        depends_on = [self._last_step_id] if self._last_step_id else []

        return self.add_step(
            name=name,
            agent_type=agent_type,
            agent_config=agent_config,
            inputs=inputs,
            depends_on=depends_on,
            timeout=timeout,
        )

    def build(self) -> Workflow:
        """Build the workflow.

        Returns:
            Complete workflow
        """
        return Workflow(
            id=self.workflow_id,
            config=self.config,
            steps=self.steps,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


# Convenience functions
def workflow(name: str, description: str = "") -> WorkflowBuilder:
    """Create a new workflow builder.

    Args:
        name: Workflow name
        description: Workflow description

    Returns:
        WorkflowBuilder instance
    """
    return WorkflowBuilder(name, description)





