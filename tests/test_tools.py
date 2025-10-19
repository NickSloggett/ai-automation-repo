"""Tests for tool functionality."""

import pytest
from src.tools.base import Tool, ToolConfig, ToolResult


class TestTool(Tool):
    """Test tool implementation."""

    async def execute(self, **kwargs) -> ToolResult:
        """Execute test tool."""
        test_input = kwargs.get("input", "")
        return ToolResult(
            success=True,
            data={"output": f"processed_{test_input}"},
            execution_time=0.1
        )


@pytest.fixture
def tool_config():
    """Create test tool configuration."""
    return ToolConfig(
        name="test_tool",
        description="A test tool",
        version="1.0.0",
        timeout=60,
        retry_on_failure=True,
        max_retries=3
    )


@pytest.mark.asyncio
async def test_tool_creation(tool_config):
    """Test tool creation."""
    tool = TestTool(tool_config)

    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert tool.config.timeout == 60


@pytest.mark.asyncio
async def test_tool_execution(tool_config):
    """Test tool execution."""
    tool = TestTool(tool_config)

    result = await tool.run(input="test_data")

    assert result.success is True
    assert result.data["output"] == "processed_test_data"
    assert result.execution_time >= 0


@pytest.mark.asyncio
async def test_tool_result_model():
    """Test tool result model."""
    result = ToolResult(
        success=True,
        data={"key": "value"},
        execution_time=1.5,
        metadata={"tool": "test"}
    )

    assert result.success is True
    assert result.data["key"] == "value"
    assert result.execution_time == 1.5
    assert result.metadata["tool"] == "test"
    assert result.error is None


@pytest.mark.asyncio
async def test_tool_error_handling(tool_config):
    """Test tool error handling."""

    class FailingTool(Tool):
        async def execute(self, **kwargs) -> ToolResult:
            raise Exception("Tool failed")

    tool = FailingTool(tool_config)
    result = await tool.run()

    assert result.success is False
    assert "Tool failed" in result.error

