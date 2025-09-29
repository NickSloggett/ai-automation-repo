"""Task-based agent for executing specific automation tasks."""

from typing import Any, Dict, List, Optional

import structlog
from pydantic import BaseModel

from .base import AgentConfig, AgentResult, BaseAgent

logger = structlog.get_logger(__name__)


class TaskConfig(AgentConfig):
    """Configuration specific to task agents."""

    task_type: str
    required_tools: List[str] = []
    output_format: str = "json"
    validate_output: bool = True


class TaskStep(BaseModel):
    """A single step in a task execution."""

    name: str
    description: str
    tool: str
    parameters: Dict[str, Any]
    expected_output: Optional[str] = None
    retry_on_failure: bool = True


class TaskAgent(BaseAgent):
    """Agent for executing structured automation tasks."""

    def __init__(self, config: TaskConfig):
        """Initialize the task agent.

        Args:
            config: Task configuration
        """
        super().__init__(config)
        self.task_config = config
        self.available_tools = {}
        self.logger = logger.bind(agent_type="task", task_type=config.task_type)

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the task using structured steps.

        Args:
            input_data: Input data containing task parameters

        Returns:
            Task execution result
        """
        try:
            # Validate input
            if not self.validate_input(input_data):
                return AgentResult(
                    success=False,
                    error="Invalid input data",
                    metadata={"agent_name": self.config.name}
                )

            # Get or generate task steps
            steps = await self._get_task_steps(input_data)

            # Execute steps
            results = []
            for step in steps:
                step_result = await self._execute_step(step, input_data)
                results.append(step_result)

                if not step_result.success and step.retry_on_failure:
                    # Retry failed steps
                    retry_result = await self._retry_step(step, input_data, step_result)
                    results[-1] = retry_result

                if not results[-1].success:
                    return AgentResult(
                        success=False,
                        error=f"Task step '{step.name}' failed",
                        data={"completed_steps": len(results), "total_steps": len(steps)},
                        metadata={"agent_name": self.config.name, "failed_step": step.name}
                    )

            # Validate final output if required
            if self.task_config.validate_output:
                validation_result = await self._validate_output(results, input_data)
                if not validation_result.success:
                    return AgentResult(
                        success=False,
                        error=f"Output validation failed: {validation_result.error}",
                        data={"results": results},
                        metadata={"agent_name": self.config.name}
                    )

            return AgentResult(
                success=True,
                data={"results": results, "steps_executed": len(results)},
                metadata={"agent_name": self.config.name}
            )

        except Exception as e:
            self.logger.error("Task execution failed", error=str(e), exc_info=True)
            return AgentResult(
                success=False,
                error=f"Task execution failed: {str(e)}",
                metadata={"agent_name": self.config.name}
            )

    async def _get_task_steps(self, input_data: Dict[str, Any]) -> List[TaskStep]:
        """Get the list of steps to execute for this task.

        Args:
            input_data: Input data for the task

        Returns:
            List of task steps to execute
        """
        # This should be overridden by subclasses for specific task types
        return [
            TaskStep(
                name="default_step",
                description="Default task step",
                tool="generic_tool",
                parameters={},
            )
        ]

    async def _execute_step(self, step: TaskStep, input_data: Dict[str, Any]) -> AgentResult:
        """Execute a single task step.

        Args:
            step: Task step to execute
            input_data: Input data for the task

        Returns:
            Step execution result
        """
        try:
            self.logger.info(
                "Executing task step",
                step_name=step.name,
                tool=step.tool
            )

            # Get the tool
            tool = self._get_tool(step.tool)
            if not tool:
                return AgentResult(
                    success=False,
                    error=f"Tool '{step.tool}' not available",
                    metadata={"step_name": step.name}
                )

            # Execute the tool
            result = await tool.execute(step.parameters, input_data)

            self.logger.info(
                "Task step completed",
                step_name=step.name,
                success=result.success
            )

            return result

        except Exception as e:
            self.logger.error(
                "Task step execution failed",
                step_name=step.name,
                error=str(e),
                exc_info=True
            )
            return AgentResult(
                success=False,
                error=f"Step execution failed: {str(e)}",
                metadata={"step_name": step.name}
            )

    async def _retry_step(
        self,
        step: TaskStep,
        input_data: Dict[str, Any],
        previous_result: AgentResult
    ) -> AgentResult:
        """Retry a failed task step.

        Args:
            step: Task step to retry
            input_data: Input data for the task
            previous_result: Previous failed result

        Returns:
            Retry result
        """
        self.logger.info(
            "Retrying task step",
            step_name=step.name,
            previous_error=previous_result.error
        )

        # Simple retry logic - could be enhanced
        return await self._execute_step(step, input_data)

    async def _validate_output(
        self,
        results: List[AgentResult],
        input_data: Dict[str, Any]
    ) -> AgentResult:
        """Validate the final output of the task.

        Args:
            results: Results from all task steps
            input_data: Original input data

        Returns:
            Validation result
        """
        # Basic validation - check that all steps succeeded
        for result in results:
            if not result.success:
                return AgentResult(
                    success=False,
                    error=f"Validation failed: step '{result.metadata.get('step_name', 'unknown')}' failed",
                    metadata={"failed_results": [r for r in results if not r.success]}
                )

        return AgentResult(success=True, data="Output validation passed")

    def _get_tool(self, tool_name: str):
        """Get a tool by name.

        Args:
            tool_name: Name of the tool to get

        Returns:
            Tool instance or None if not found
        """
        return self.available_tools.get(tool_name)

    def register_tool(self, tool_name: str, tool):
        """Register a tool for use by this agent.

        Args:
            tool_name: Name of the tool
            tool: Tool instance
        """
        self.available_tools[tool_name] = tool
        self.logger.info("Tool registered", tool_name=tool_name)

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for task execution.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid, False otherwise
        """
        # Check required fields based on task type
        required_fields = getattr(self.task_config, 'required_input_fields', [])
        for field in required_fields:
            if field not in input_data:
                self.logger.error("Missing required input field", field=field)
                return False

        return True
