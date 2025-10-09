"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..config import get_settings

settings = get_settings()


class LLMMessage(BaseModel):
    """Message for LLM chat."""

    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None


class LLMResponse(BaseModel):
    """Response from LLM."""

    content: str
    model: str
    usage: Dict[str, int] = {}
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseLLM(ABC):
    """Base class for LLM providers."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs: Any):
        """Initialize the LLM provider.

        Args:
            model: Model name to use
            api_key: API key for the provider
            **kwargs: Additional provider-specific arguments
        """
        self.model = model or settings.llm.model
        self.api_key = api_key or settings.llm.api_key
        self.temperature = kwargs.get("temperature", settings.llm.temperature)
        self.max_tokens = kwargs.get("max_tokens", settings.llm.max_tokens)
        self.timeout = kwargs.get("timeout", settings.llm.request_timeout)
        self.settings = settings
        self.extra_kwargs = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text from a prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters

        Returns:
            LLMResponse with generated text
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Chat with the LLM using message history.

        Args:
            messages: List of messages in the conversation
            **kwargs: Additional generation parameters

        Returns:
            LLMResponse with generated text
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Stream text generation from a prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters

        Yields:
            Chunks of generated text
        """
        pass

    def _merge_kwargs(self, **kwargs: Any) -> Dict[str, Any]:
        """Merge provider kwargs with call-specific kwargs.

        Args:
            **kwargs: Call-specific kwargs

        Returns:
            Merged kwargs dictionary
        """
        merged = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }
        merged.update(self.extra_kwargs)
        merged.update(kwargs)
        return merged







