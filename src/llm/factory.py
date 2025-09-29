"""LLM provider factory."""

from typing import Any, Optional

import structlog

from ..config import get_settings
from .anthropic_provider import AnthropicProvider
from .base import BaseLLM
from .groq_provider import GroqProvider
from .local_provider import LocalProvider
from .openai_provider import OpenAIProvider

settings = get_settings()
logger = structlog.get_logger(__name__)


def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> BaseLLM:
    """Get an LLM provider instance.

    Args:
        provider: Provider name (openai, anthropic, groq, local)
        model: Model name to use
        api_key: API key for the provider
        **kwargs: Additional provider-specific arguments

    Returns:
        LLM provider instance

    Raises:
        ValueError: If provider is not supported
    """
    provider = (provider or settings.llm.provider).lower()

    logger.info("Initializing LLM provider", provider=provider, model=model or settings.llm.model)

    if provider == "openai":
        return OpenAIProvider(model=model, api_key=api_key, **kwargs)
    elif provider == "anthropic":
        return AnthropicProvider(model=model, api_key=api_key, **kwargs)
    elif provider == "groq":
        return GroqProvider(model=model, api_key=api_key, **kwargs)
    elif provider == "local":
        return LocalProvider(model=model, api_key=api_key, **kwargs)
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, anthropic, groq, local"
        )
