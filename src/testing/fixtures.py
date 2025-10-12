"""Testing fixtures and utilities."""

from typing import Dict, Any, Optional

from ..agents.base import AgentConfig
from ..agents.task import TaskAgent
from .agent_tester import AgentTester, TestScenario


def create_test_agent(
    name: str = "test_agent",
    description: str = "Test agent",
    **config_kwargs
) -> TaskAgent:
    """Create a test agent instance."""
    config = AgentConfig(
        name=name,
        description=description,
        enable_caching=False,  # Disable caching for tests
        **config_kwargs
    )
    return TaskAgent(config)


def create_test_scenario(
    name: str,
    input_data: Dict[str, Any],
    expected_output: Optional[Any] = None,
    expected_success: bool = True,
    **kwargs
) -> TestScenario:
    """Create a test scenario."""
    return TestScenario(
        name=name,
        input_data=input_data,
        expected_output=expected_output,
        expected_success=expected_success,
        **kwargs
    )


def create_llm_mock_responses(llm_mocker):
    """Setup common LLM mock responses."""
    # Success responses
    llm_mocker.add_simple_response(
        content="Task completed successfully.",
        input_pattern=r"process.*email"
    )

    llm_mocker.add_simple_response(
        content="Analysis complete. Key insights: revenue up 15%.",
        input_pattern=r"analyze.*data"
    )

    # Error responses
    llm_mocker.add_simple_response(
        content="Error: Invalid input format.",
        input_pattern=r"invalid.*input"
    )

    # Default response
    llm_mocker.set_default_response("Mock response generated.")
