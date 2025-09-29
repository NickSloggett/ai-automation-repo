"""Groq LLM provider implementation."""

from typing import Any, List, Optional

import structlog
from groq import AsyncGroq

from .base import BaseLLM, LLMMessage, LLMResponse

logger = structlog.get_logger(__name__)


class GroqProvider(BaseLLM):
    """Groq LLM provider."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs: Any):
        """Initialize Groq provider."""
        super().__init__(model=model or "mixtral-8x7b-32768", api_key=api_key, **kwargs)
        self.client = AsyncGroq(api_key=self.api_key, timeout=self.timeout)
        logger.info("Groq provider initialized", model=self.model)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text using Groq."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        merged_kwargs = self._merge_kwargs(**kwargs)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=merged_kwargs["temperature"],
                max_tokens=merged_kwargs["max_tokens"],
            )

            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                finish_reason=response.choices[0].finish_reason,
                metadata={"response_id": response.id},
            )

        except Exception as e:
            logger.error("Groq generation failed", error=str(e), exc_info=True)
            raise

    async def chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Chat with Groq."""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        merged_kwargs = self._merge_kwargs(**kwargs)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=merged_kwargs["temperature"],
                max_tokens=merged_kwargs["max_tokens"],
            )

            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                finish_reason=response.choices[0].finish_reason,
                metadata={"response_id": response.id},
            )

        except Exception as e:
            logger.error("Groq chat failed", error=str(e), exc_info=True)
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Stream text generation from Groq."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        merged_kwargs = self._merge_kwargs(**kwargs)

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=merged_kwargs["temperature"],
                max_tokens=merged_kwargs["max_tokens"],
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error("Groq streaming failed", error=str(e), exc_info=True)
            raise
