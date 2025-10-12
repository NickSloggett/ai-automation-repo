"""OpenAI LLM provider implementation."""

from typing import Any, List, Optional

import structlog
from openai import AsyncOpenAI

from ..caching import get_cache_manager
from ..circuit_breaker import circuit_breaker
from ..cost_tracking import track_llm_cost
from .base import BaseLLM, LLMMessage, LLMResponse

logger = structlog.get_logger(__name__)


class OpenAIProvider(BaseLLM):
    """OpenAI LLM provider."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs: Any):
        """Initialize OpenAI provider."""
        super().__init__(model=model, api_key=api_key, **kwargs)
        self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout)
        self.cache_manager = None  # Will be initialized lazily
        logger.info("OpenAI provider initialized", model=self.model)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text using OpenAI with caching support."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        merged_kwargs = self._merge_kwargs(**kwargs)

        # Check cache first
        cached_response = await self._get_cached_response(prompt, system_prompt, merged_kwargs)
        if cached_response:
            logger.info("Using cached LLM response", cache_hit=True)
            return cached_response

        try:
            response = await self._call_with_circuit_breaker(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=merged_kwargs["temperature"],
                max_tokens=merged_kwargs["max_tokens"],
            )

            llm_response = LLMResponse(
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

            # Track costs
            await track_llm_cost(
                model=response.model,
                provider="openai",
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                agent_name=kwargs.get("agent_name"),
                user_id=kwargs.get("user_id"),
                session_id=kwargs.get("session_id"),
            )

            # Cache the response
            await self._cache_response(prompt, system_prompt, merged_kwargs, llm_response)

            return llm_response

        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e), exc_info=True)
            raise

    async def chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Chat with OpenAI."""
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
            logger.error("OpenAI chat failed", error=str(e), exc_info=True)
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Stream text generation from OpenAI."""
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
            logger.error("OpenAI streaming failed", error=str(e), exc_info=True)
            raise

    async def _get_cached_response(
        self,
        prompt: str,
        system_prompt: Optional[str],
        kwargs: dict
    ) -> Optional[LLMResponse]:
        """Get cached LLM response if available."""
        try:
            if self.cache_manager is None:
                self.cache_manager = await get_cache_manager()

            # Use LLM cache strategy
            strategy = self.cache_manager.get_strategy("llm")
            if not strategy:
                from ..caching.strategies import LLMCacheStrategy
                strategy = LLMCacheStrategy(self.cache_manager)
                self.cache_manager.register_strategy("llm", strategy)

            cache_key = strategy.generate_key(prompt, self.model, **kwargs)
            cached_data = await strategy.get(cache_key)

            if cached_data:
                return LLMResponse(**cached_data)

        except Exception as e:
            logger.warning("Failed to get cached LLM response", error=str(e))

        return None

    async def _cache_response(
        self,
        prompt: str,
        system_prompt: Optional[str],
        kwargs: dict,
        response: LLMResponse
    ) -> None:
        """Cache LLM response."""
        try:
            if self.cache_manager is None:
                self.cache_manager = await get_cache_manager()

            # Use LLM cache strategy
            strategy = self.cache_manager.get_strategy("llm")
            if not strategy:
                from ..caching.strategies import LLMCacheStrategy
                strategy = LLMCacheStrategy(self.cache_manager)
                self.cache_manager.register_strategy("llm", strategy)

            cache_key = strategy.generate_key(prompt, self.model, **kwargs)
            await strategy.set(cache_key, response.dict())

        except Exception as e:
            logger.warning("Failed to cache LLM response", error=str(e))

    @circuit_breaker(
        failure_threshold=5,
        recovery_timeout=60.0,
        timeout=30.0,
        name="openai_api"
    )
    async def _call_with_circuit_breaker(self, func, **kwargs):
        """Call OpenAI API with circuit breaker protection."""
        return await func(**kwargs)


