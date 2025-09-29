"""Anthropic (Claude) LLM provider implementation."""

from typing import Any, List, Optional

import structlog
from anthropic import AsyncAnthropic

from .base import BaseLLM, LLMMessage, LLMResponse

logger = structlog.get_logger(__name__)


class AnthropicProvider(BaseLLM):
    """Anthropic (Claude) LLM provider."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs: Any):
        """Initialize Anthropic provider."""
        super().__init__(model=model or "claude-3-sonnet-20240229", api_key=api_key, **kwargs)
        self.client = AsyncAnthropic(api_key=self.api_key, timeout=self.timeout)
        logger.info("Anthropic provider initialized", model=self.model)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text using Anthropic."""
        merged_kwargs = self._merge_kwargs(**kwargs)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=merged_kwargs["max_tokens"],
                temperature=merged_kwargs["temperature"],
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
                metadata={"response_id": response.id},
            )

        except Exception as e:
            logger.error("Anthropic generation failed", error=str(e), exc_info=True)
            raise

    async def chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Chat with Anthropic."""
        # Extract system message if present
        system_message = ""
        formatted_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        merged_kwargs = self._merge_kwargs(**kwargs)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=merged_kwargs["max_tokens"],
                temperature=merged_kwargs["temperature"],
                system=system_message,
                messages=formatted_messages,
            )

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
                metadata={"response_id": response.id},
            )

        except Exception as e:
            logger.error("Anthropic chat failed", error=str(e), exc_info=True)
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Stream text generation from Anthropic."""
        merged_kwargs = self._merge_kwargs(**kwargs)

        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=merged_kwargs["max_tokens"],
                temperature=merged_kwargs["temperature"],
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error("Anthropic streaming failed", error=str(e), exc_info=True)
            raise
