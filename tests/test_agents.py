"""Tests for agent functionality."""

import pytest
from src.agents.base import AgentConfig, AgentResult
from src.agents.task import TaskAgent, TaskConfig, TaskStep
from src.agents.decision import DecisionAgent, DecisionConfig


@pytest.mark.asyncio
async def test_base_agent_config(sample_agent_config):
    """Test agent configuration creation."""
    config = AgentConfig(**sample_agent_config)
    assert config.name == "test_agent"
    assert config.max_retries == 3
    assert config.timeout == 300


@pytest.mark.asyncio
async def test_task_agent_creation(sample_task_config):
    """Test task agent creation."""
    config = TaskConfig(**sample_task_config)
    agent = TaskAgent(config)

    assert agent.config.name == "test_task_agent"
    assert agent.task_config.task_type == "email_processing"
    assert len(agent.task_config.required_tools) == 2


@pytest.mark.asyncio
async def test_task_agent_validation(sample_task_config):
    """Test task agent input validation."""
    # Create config with required fields
    config_dict = sample_task_config.copy()
    config_dict["required_input_fields"] = ["email_id", "content"]
    config = TaskConfig(**config_dict)
    agent = TaskAgent(config)

    # Valid input
    valid_input = {"email_id": "123", "content": "Test email"}
    assert agent.validate_input(valid_input) is True

    # Invalid input (missing field)
    invalid_input = {"email_id": "123"}
    assert agent.validate_input(invalid_input) is False


@pytest.mark.asyncio
async def test_decision_agent_creation(sample_decision_config):
    """Test decision agent creation."""
    config = DecisionConfig(**sample_decision_config)
    agent = DecisionAgent(config)

    assert agent.config.name == "test_decision_agent"
    assert agent.decision_config.confidence_threshold == 0.8
    assert len(agent.decision_config.decision_criteria) == 3


@pytest.mark.asyncio
async def test_decision_agent_validation(sample_decision_config):
    """Test decision agent input validation."""
    config = DecisionConfig(**sample_decision_config)
    agent = DecisionAgent(config)

    # Valid input
    valid_input = {"situation": "Test situation", "constraints": []}
    assert agent.validate_input(valid_input) is True

    # Invalid input (missing situation)
    invalid_input = {"constraints": []}
    assert agent.validate_input(invalid_input) is False


@pytest.mark.asyncio
async def test_agent_result_creation():
    """Test agent result model."""
    result = AgentResult(
        success=True,
        data={"key": "value"},
        execution_time=1.5,
        metadata={"agent_name": "test"},
    )

    assert result.success is True
    assert result.data["key"] == "value"
    assert result.execution_time == 1.5
    assert result.error is None


@pytest.mark.asyncio
async def test_task_step_creation():
    """Test task step model."""
    step = TaskStep(
        name="test_step",
        description="Test step description",
        tool="test_tool",
        parameters={"param1": "value1"},
        expected_output="json",
        retry_on_failure=True,
    )

    assert step.name == "test_step"
    assert step.tool == "test_tool"
    assert step.retry_on_failure is True







