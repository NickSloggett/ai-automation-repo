"""LLM response mocking for testing."""

import re
from typing import Any, Dict, List, Optional, Pattern, Union
from unittest.mock import AsyncMock, MagicMock

from ..llm.base import LLMResponse


class MockResponse:
    """Mock LLM response with pattern matching."""

    def __init__(
        self,
        content: str,
        model: Optional[str] = None,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: str = "stop",
        metadata: Optional[Dict[str, Any]] = None,
        # Pattern matching
        input_pattern: Optional[Union[str, Pattern]] = None,
        system_prompt_pattern: Optional[Union[str, Pattern]] = None,
        kwargs_pattern: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.model = model or "gpt-3.5-turbo"
        self.usage = usage or {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        self.finish_reason = finish_reason
        self.metadata = metadata or {}

        # Pattern matching for conditional responses
        self.input_pattern = self._compile_pattern(input_pattern)
        self.system_prompt_pattern = self._compile_pattern(system_prompt_pattern)
        self.kwargs_pattern = kwargs_pattern

    def _compile_pattern(self, pattern: Optional[Union[str, Pattern]]) -> Optional[Pattern]:
        """Compile string pattern to regex."""
        if isinstance(pattern, str):
            return re.compile(pattern, re.IGNORECASE)
        return pattern

    def matches(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Check if this mock response matches the input."""
        # Check input pattern
        if self.input_pattern and not self.input_pattern.search(prompt):
            return False

        # Check system prompt pattern
        if self.system_prompt_pattern:
            if not system_prompt or not self.system_prompt_pattern.search(system_prompt):
                return False

        # Check kwargs pattern
        if self.kwargs_pattern:
            for key, expected_value in self.kwargs_pattern.items():
                actual_value = kwargs.get(key)
                if actual_value != expected_value:
                    return False

        return True

    def to_llm_response(self) -> LLMResponse:
        """Convert to LLMResponse."""
        return LLMResponse(
            content=self.content,
            model=self.model,
            usage=self.usage,
            finish_reason=self.finish_reason,
            metadata=self.metadata,
        )


class LLMMocker:
    """Mock LLM provider for testing."""

    def __init__(self):
        self.mock_responses: List[MockResponse] = []
        self.call_history: List[Dict[str, Any]] = []
        self.default_response = MockResponse("This is a default mock response.")

    def add_response(self, mock_response: MockResponse) -> None:
        """Add a mock response."""
        self.mock_responses.append(mock_response)

    def add_simple_response(
        self,
        content: str,
        input_pattern: Optional[str] = None,
        **kwargs
    ) -> None:
        """Add a simple mock response."""
        mock_response = MockResponse(content=content, input_pattern=input_pattern, **kwargs)
        self.add_response(mock_response)

    def set_default_response(self, content: str, **kwargs) -> None:
        """Set the default response when no patterns match."""
        self.default_response = MockResponse(content=content, **kwargs)

    def find_matching_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> MockResponse:
        """Find the first matching mock response."""
        for mock_response in self.mock_responses:
            if mock_response.matches(prompt, system_prompt, **kwargs):
                return mock_response

        return self.default_response

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Mock generate method."""
        # Record the call
        self.call_history.append({
            "method": "generate",
            "prompt": prompt,
            "system_prompt": system_prompt,
            "kwargs": kwargs,
            "timestamp": self._get_timestamp(),
        })

        # Find matching response
        mock_response = self.find_matching_response(prompt, system_prompt, **kwargs)
        return mock_response.to_llm_response()

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> LLMResponse:
        """Mock chat method."""
        # Convert messages to prompt for pattern matching
        prompt = " ".join([msg.get("content", "") for msg in messages if msg.get("role") == "user"])
        system_prompt = next(
            (msg.get("content", "") for msg in messages if msg.get("role") == "system"),
            None
        )

        # Record the call
        self.call_history.append({
            "method": "chat",
            "messages": messages,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "kwargs": kwargs,
            "timestamp": self._get_timestamp(),
        })

        # Find matching response
        mock_response = self.find_matching_response(prompt, system_prompt, **kwargs)
        return mock_response.to_llm_response()

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Mock streaming method."""
        response = await self.generate(prompt, system_prompt, **kwargs)
        # Yield content in chunks
        words = response.content.split()
        for word in words:
            yield word + " "

    def get_call_history(self) -> List[Dict[str, Any]]:
        """Get call history."""
        return self.call_history.copy()

    def clear_call_history(self) -> None:
        """Clear call history."""
        self.call_history.clear()

    def get_call_count(self, method: Optional[str] = None) -> int:
        """Get call count for a method."""
        if method:
            return sum(1 for call in self.call_history if call["method"] == method)
        return len(self.call_history)

    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()

    def create_mock_provider(self):
        """Create a mock provider instance."""
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=self.generate)
        mock_provider.chat = AsyncMock(side_effect=self.chat)
        mock_provider.stream = self.stream  # Not async for simplicity
        return mock_provider
