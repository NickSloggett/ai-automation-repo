"""Base agent implementation for AI automation tasks."""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import structlog
from pydantic import BaseModel

from ..config import get_settings
from ..monitoring import track_performance


logger = structlog.get_logger(__name__)


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str
    description: str
    max_retries: int = 3
    timeout: int = 300
    enable_caching: bool = True
    cache_ttl: int = 3600


class AgentResult(BaseModel):
    """Result from an agent execution."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
    execution_time: float = 0.0


class BaseAgent(ABC):
    """Base class for all AI automation agents."""

    def __init__(self, config: AgentConfig):
        """Initialize the agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.settings = get_settings()
        self.logger = logger.bind(agent_name=config.name)

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent's main task.

        Args:
            input_data: Input data for the agent

        Returns:
            Agent execution result
        """
        pass

    async def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """Run the agent with error handling and monitoring.

        Args:
            input_data: Input data for the agent

        Returns:
            Agent execution result
        """
        start_time = time.time()

        try:
            self.logger.info("Starting agent execution", input_keys=list(input_data.keys()))

            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute(input_data),
                timeout=self.config.timeout
            )

            execution_time = time.time() - start_time

            # Update result with execution time
            result.execution_time = execution_time
            result.metadata.update({
                "agent_name": self.config.name,
                "execution_time": execution_time,
                "timeout": self.config.timeout,
            })

            self.logger.info(
                "Agent execution completed successfully",
                execution_time=execution_time,
                success=result.success
            )

            return result

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Agent execution timed out after {self.config.timeout} seconds"

            self.logger.error(error_msg, agent_name=self.config.name)

            return AgentResult(
                success=False,
                error=error_msg,
                execution_time=execution_time,
                metadata={
                    "agent_name": self.config.name,
                    "execution_time": execution_time,
                    "timeout": self.config.timeout,
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Agent execution failed: {str(e)}"

            self.logger.error(
                error_msg,
                agent_name=self.config.name,
                error_type=type(e).__name__,
                exc_info=True
            )

            return AgentResult(
                success=False,
                error=error_msg,
                execution_time=execution_time,
                metadata={
                    "agent_name": self.config.name,
                    "execution_time": execution_time,
                    "error_type": type(e).__name__,
                }
            )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the agent.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid, False otherwise
        """
        # Override in subclasses for specific validation
        return True

    def get_cache_key(self, input_data: Dict[str, Any]) -> str:
        """Generate a cache key for the input data.

        Args:
            input_data: Input data to generate cache key for

        Returns:
            Cache key string
        """
        # Simple cache key generation - override for more complex scenarios
        return str(hash(str(sorted(input_data.items()))))

    async def get_cached_result(self, cache_key: str) -> Optional[AgentResult]:
        """Get cached result if available.

        Args:
            cache_key: Cache key to look up

        Returns:
            Cached result or None if not found
        """
        # Override in subclasses to implement caching
        return None

    async def cache_result(self, cache_key: str, result: AgentResult) -> None:
        """Cache the result.

        Args:
            cache_key: Cache key
            result: Result to cache
        """
        # Override in subclasses to implement caching
        pass

    async def execute_with_retry(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent with retry logic.

        Args:
            input_data: Input data for the agent

        Returns:
            Agent execution result
        """
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(
                        "Retrying agent execution",
                        attempt=attempt,
                        max_retries=self.config.max_retries
                    )

                result = await self.run(input_data)
                return result

            except Exception as e:
                last_exception = e

                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(
                        "Agent execution failed, retrying",
                        attempt=attempt + 1,
                        max_retries=self.config.max_retries,
                        wait_time=wait_time,
                        error=str(e)
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(
                        "Agent execution failed after all retries",
                        attempt=attempt + 1,
                        max_retries=self.config.max_retries,
                        error=str(e)
                    )

        # If we get here, all retries failed
        return AgentResult(
            success=False,
            error=f"Agent failed after {self.config.max_retries + 1} attempts: {str(last_exception)}",
            metadata={
                "agent_name": self.config.name,
                "max_retries": self.config.max_retries,
            }
        )
