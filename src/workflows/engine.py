"""Workflow execution engine."""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from ..agents.base import BaseAgent, AgentResult
from ..agents.task import TaskAgent, TaskConfig
from ..agents.decision import DecisionAgent, DecisionConfig
from .models import (
    Workflow,
    WorkflowStep,
    WorkflowResult,
    StepResult,
    WorkflowStatus,
    WorkflowExecutionContext,
)

logger = structlog.get_logger(__name__)


class WorkflowEngine:
    """Engine for executing workflows."""

    def __init__(self):
        """Initialize workflow engine."""
        self.logger = logger.bind(component="workflow_engine")
        self.running_workflows: Dict[str, WorkflowExecutionContext] = {}

    async def execute(
        self,
        workflow: Workflow,
        initial_input: Dict[str, Any] = None,
    ) -> WorkflowResult:
        """Execute a workflow.

        Args:
            workflow: Workflow to execute
            initial_input: Initial input data

        Returns:
            Workflow execution result
        """
        start_time = time.time()
        context = WorkflowExecutionContext(
            workflow_id=workflow.id,
            variables=initial_input or {},
        )
        self.running_workflows[workflow.id] = context

        result = WorkflowResult(
            workflow_id=workflow.id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.utcnow(),
        )

        try:
            self.logger.info(
                "Starting workflow execution",
                workflow_id=workflow.id,
                workflow_name=workflow.config.name,
                num_steps=len(workflow.steps),
            )

            # Build dependency graph
            dependency_graph = self._build_dependency_graph(workflow.steps)

            # Execute steps in order
            for step_batch in dependency_graph:
                if workflow.config.parallel_execution and len(step_batch) > 1:
                    # Execute steps in parallel
                    batch_results = await self._execute_step_batch_parallel(
                        step_batch, workflow, context
                    )
                else:
                    # Execute steps sequentially
                    batch_results = await self._execute_step_batch_sequential(
                        step_batch, workflow, context
                    )

                # Store results
                for step_id, step_result in batch_results.items():
                    result.step_results[step_id] = step_result
                    context.completed_steps.append(step_id)

                    if step_result.output:
                        context.step_outputs[step_id] = step_result.output

                    # Check for failures
                    if step_result.status == WorkflowStatus.FAILED:
                        if workflow.config.on_failure == "stop":
                            result.status = WorkflowStatus.FAILED
                            result.error = f"Step {step_id} failed: {step_result.error}"
                            break
                        elif workflow.config.on_failure == "rollback":
                            await self._rollback_workflow(workflow, context)
                            result.status = WorkflowStatus.FAILED
                            result.error = f"Workflow rolled back due to step {step_id} failure"
                            break

                if result.status == WorkflowStatus.FAILED:
                    break

            # Set final status
            if result.status != WorkflowStatus.FAILED:
                result.status = WorkflowStatus.COMPLETED
                # Get final output from last step
                if workflow.steps:
                    last_step_id = workflow.steps[-1].id
                    result.final_output = context.step_outputs.get(last_step_id)

        except asyncio.TimeoutError:
            result.status = WorkflowStatus.FAILED
            result.error = f"Workflow execution timed out after {workflow.config.timeout} seconds"
            self.logger.error("Workflow timeout", workflow_id=workflow.id)

        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.error = f"Workflow execution failed: {str(e)}"
            self.logger.error(
                "Workflow execution failed",
                workflow_id=workflow.id,
                error=str(e),
                exc_info=True,
            )

        finally:
            result.completed_at = datetime.utcnow()
            result.total_execution_time = time.time() - start_time

            if workflow.id in self.running_workflows:
                del self.running_workflows[workflow.id]

            self.logger.info(
                "Workflow execution completed",
                workflow_id=workflow.id,
                status=result.status,
                execution_time=result.total_execution_time,
            )

        return result

    def _build_dependency_graph(
        self, steps: List[WorkflowStep]
    ) -> List[List[WorkflowStep]]:
        """Build dependency graph for parallel execution.

        Args:
            steps: Workflow steps

        Returns:
            List of step batches that can be executed in parallel
        """
        # Simple implementation: group steps by dependency level
        step_dict = {step.id: step for step in steps}
        levels: List[List[WorkflowStep]] = []
        completed = set()

        while len(completed) < len(steps):
            current_level = []

            for step in steps:
                if step.id in completed:
                    continue

                # Check if all dependencies are completed
                if all(dep in completed for dep in step.depends_on):
                    current_level.append(step)

            if not current_level:
                # Circular dependency or missing dependencies
                remaining = [s for s in steps if s.id not in completed]
                self.logger.warning(
                    "Circular or missing dependencies detected",
                    remaining_steps=[s.id for s in remaining],
                )
                break

            levels.append(current_level)
            completed.update(step.id for step in current_level)

        return levels

    async def _execute_step_batch_parallel(
        self,
        steps: List[WorkflowStep],
        workflow: Workflow,
        context: WorkflowExecutionContext,
    ) -> Dict[str, StepResult]:
        """Execute a batch of steps in parallel.

        Args:
            steps: Steps to execute
            workflow: Parent workflow
            context: Execution context

        Returns:
            Dictionary of step results
        """
        tasks = [
            self._execute_step(step, workflow, context) for step in steps
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            step.id: result if not isinstance(result, Exception) else StepResult(
                step_id=step.id,
                status=WorkflowStatus.FAILED,
                error=str(result),
            )
            for step, result in zip(steps, results)
        }

    async def _execute_step_batch_sequential(
        self,
        steps: List[WorkflowStep],
        workflow: Workflow,
        context: WorkflowExecutionContext,
    ) -> Dict[str, StepResult]:
        """Execute a batch of steps sequentially.

        Args:
            steps: Steps to execute
            workflow: Parent workflow
            context: Execution context

        Returns:
            Dictionary of step results
        """
        results = {}
        for step in steps:
            result = await self._execute_step(step, workflow, context)
            results[step.id] = result

        return results

    async def _execute_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
        context: WorkflowExecutionContext,
    ) -> StepResult:
        """Execute a single workflow step.

        Args:
            step: Step to execute
            workflow: Parent workflow
            context: Execution context

        Returns:
            Step execution result
        """
        start_time = time.time()
        context.current_step = step.id

        self.logger.info(
            "Executing workflow step",
            workflow_id=workflow.id,
            step_id=step.id,
            step_name=step.name,
        )

        try:
            # Check condition
            if step.condition and not self._evaluate_condition(step.condition, context):
                self.logger.info("Step condition not met, skipping", step_id=step.id)
                return StepResult(
                    step_id=step.id,
                    status=WorkflowStatus.COMPLETED,
                    output={"skipped": True, "reason": "condition_not_met"},
                    execution_time=0.0,
                )

            # Resolve inputs from context
            inputs = self._resolve_inputs(step.inputs, context)

            # Create agent
            agent = self._create_agent(step)

            # Execute agent
            agent_result = await asyncio.wait_for(
                agent.execute(inputs),
                timeout=step.timeout,
            )

            execution_time = time.time() - start_time

            if agent_result.success:
                return StepResult(
                    step_id=step.id,
                    status=WorkflowStatus.COMPLETED,
                    output=agent_result.data,
                    execution_time=execution_time,
                    metadata=agent_result.metadata,
                )
            else:
                return StepResult(
                    step_id=step.id,
                    status=WorkflowStatus.FAILED,
                    error=agent_result.error,
                    execution_time=execution_time,
                    metadata=agent_result.metadata,
                )

        except asyncio.TimeoutError:
            return StepResult(
                step_id=step.id,
                status=WorkflowStatus.FAILED,
                error=f"Step execution timed out after {step.timeout} seconds",
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            self.logger.error(
                "Step execution failed",
                step_id=step.id,
                error=str(e),
                exc_info=True,
            )
            return StepResult(
                step_id=step.id,
                status=WorkflowStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time,
            )

    def _create_agent(self, step: WorkflowStep) -> BaseAgent:
        """Create agent for step execution.

        Args:
            step: Workflow step

        Returns:
            Agent instance
        """
        if step.agent_type == "task":
            config = TaskConfig(**step.agent_config)
            return TaskAgent(config)
        elif step.agent_type == "decision":
            config = DecisionConfig(**step.agent_config)
            return DecisionAgent(config)
        else:
            raise ValueError(f"Unknown agent type: {step.agent_type}")

    def _resolve_inputs(
        self,
        inputs: Dict[str, Any],
        context: WorkflowExecutionContext,
    ) -> Dict[str, Any]:
        """Resolve step inputs from context.

        Args:
            inputs: Input template
            context: Execution context

        Returns:
            Resolved inputs
        """
        resolved = {}

        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Template variable
                var_path = value[2:-2].strip()
                resolved[key] = self._get_context_value(var_path, context)
            else:
                resolved[key] = value

        return resolved

    def _get_context_value(self, path: str, context: WorkflowExecutionContext) -> Any:
        """Get value from context by path.

        Args:
            path: Dot-separated path (e.g., "step1.output.result")
            context: Execution context

        Returns:
            Value from context
        """
        parts = path.split(".")

        if parts[0] in context.step_outputs:
            value = context.step_outputs[parts[0]]
            for part in parts[1:]:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            return value

        return context.variables.get(path)

    def _evaluate_condition(self, condition, context: WorkflowExecutionContext) -> bool:
        """Evaluate step condition.

        Args:
            condition: Condition to evaluate
            context: Execution context

        Returns:
            True if condition is met
        """
        value = self._get_context_value(condition.field, context)

        if condition.operator == "equals":
            return value == condition.value
        elif condition.operator == "not_equals":
            return value != condition.value
        elif condition.operator == "contains":
            return condition.value in str(value)
        elif condition.operator == "greater_than":
            return float(value) > float(condition.value)
        elif condition.operator == "less_than":
            return float(value) < float(condition.value)
        else:
            return False

    async def _rollback_workflow(
        self,
        workflow: Workflow,
        context: WorkflowExecutionContext,
    ):
        """Rollback workflow execution.

        Args:
            workflow: Workflow to rollback
            context: Execution context
        """
        self.logger.info("Rolling back workflow", workflow_id=workflow.id)
        # Implement rollback logic here
        # This could involve calling cleanup methods on agents
        # or restoring previous state





