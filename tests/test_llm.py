"""Tests for LLM integrations."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.llm import LLMMessage, LLMResponse
from src.llm.factory import get_llm


@pytest.mark.asyncio
async def test_llm_message_creation():
    """Test LLM message model."""
    message = LLMMessage(role="user", content="Hello, world!")
    assert message.role == "user"
    assert message.content == "Hello, world!"


@pytest.mark.asyncio
async def test_llm_response_creation():
    """Test LLM response model."""
    response = LLMResponse(
        content="Hello from AI!",
        model="gpt-3.5-turbo",
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        finish_reason="stop",
    )

    assert response.content == "Hello from AI!"
    assert response.model == "gpt-3.5-turbo"
    assert response.usage["total_tokens"] == 15


@pytest.mark.asyncio
async def test_get_llm_factory():
    """Test LLM factory."""
    # Test getting different providers
    with patch('src.llm.factory.settings') as mock_settings:
        mock_settings.llm.provider = "openai"
        mock_settings.llm.model = "gpt-3.5-turbo"
        mock_settings.llm.api_key = "test-key"
        mock_settings.llm.temperature = 0.7
        mock_settings.llm.max_tokens = 2048
        mock_settings.llm.request_timeout = 60

        llm = get_llm(provider="openai", api_key="test-key")
        assert llm is not None
        assert llm.model == "gpt-3.5-turbo"


@pytest.mark.asyncio
async def test_get_llm_invalid_provider():
    """Test LLM factory with invalid provider."""
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm(provider="invalid_provider")
