"""Base tool interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel
import time


class ToolConfig(BaseModel):
    """Tool configuration."""

    name: str
    description: str
    version: str = "1.0.0"
    timeout: int = 60
    retry_on_failure: bool = True
    max_retries: int = 3


class ToolResult(BaseModel):
    """Result from tool execution."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = {}


class Tool(ABC):
    """Base class for all tools."""

    def __init__(self, config: ToolConfig):
        """Initialize tool.

        Args:
            config: Tool configuration
        """
        self.config = config

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result
        """
        pass

    async def run(self, **kwargs) -> ToolResult:
        """Run the tool with error handling.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result
        """
        start_time = time.time()

        try:
            result = await self.execute(**kwargs)
            result.execution_time = time.time() - start_time
            return result

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
            )

    def validate_input(self, **kwargs) -> bool:
        """Validate tool input.

        Args:
            **kwargs: Input parameters

        Returns:
            True if valid
        """
        return True

    @property
    def name(self) -> str:
        """Get tool name."""
        return self.config.name

    @property
    def description(self) -> str:
        """Get tool description."""
        return self.config.description





