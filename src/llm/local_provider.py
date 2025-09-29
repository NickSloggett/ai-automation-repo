"""Local LLM provider implementation (for Ollama, etc.)."""

from typing import Any, List, Optional

import httpx
import structlog

from .base import BaseLLM, LLMMessage, LLMResponse

logger = structlog.get_logger(__name__)


class LocalProvider(BaseLLM):
    """Local LLM provider (Ollama, LM Studio, etc.)."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs: Any):
        """Initialize Local provider."""
        super().__init__(model=model or "llama2", api_key=api_key, **kwargs)
        self.base_url = kwargs.get("base_url", "http://localhost:11434")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        logger.info("Local provider initialized", model=self.model, base_url=self.base_url)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text using local LLM."""
        merged_kwargs = self._merge_kwargs(**kwargs)

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": merged_kwargs["temperature"],
                "num_predict": merged_kwargs["max_tokens"],
            },
        }

        try:
            response = await self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data.get("response", ""),
                model=self.model,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
                finish_reason="stop",
                metadata={"context": data.get("context", [])},
            )

        except Exception as e:
            logger.error("Local LLM generation failed", error=str(e), exc_info=True)
            raise

    async def chat(
        self,
        messages: List[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Chat with local LLM."""
        merged_kwargs = self._merge_kwargs(**kwargs)

        payload = {
            "model": self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "stream": False,
            "options": {
                "temperature": merged_kwargs["temperature"],
                "num_predict": merged_kwargs["max_tokens"],
            },
        }

        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data.get("message", {}).get("content", ""),
                model=self.model,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
                finish_reason="stop",
                metadata={"context": data.get("context", [])},
            )

        except Exception as e:
            logger.error("Local LLM chat failed", error=str(e), exc_info=True)
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Stream text generation from local LLM."""
        merged_kwargs = self._merge_kwargs(**kwargs)

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": merged_kwargs["temperature"],
                "num_predict": merged_kwargs["max_tokens"],
            },
        }

        try:
            async with self.client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]

        except Exception as e:
            logger.error("Local LLM streaming failed", error=str(e), exc_info=True)
            raise

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
