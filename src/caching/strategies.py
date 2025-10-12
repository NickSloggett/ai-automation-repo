"""Cache strategies for different use cases."""

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

from ..config import get_settings
from .cache_manager import BaseCacheStrategy, CacheManager


class LLMCacheStrategy(BaseCacheStrategy):
    """Cache strategy optimized for LLM responses."""

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get LLM response from cache."""
        cached_data = await self.cache_manager.get(f"llm:{key}")
        if cached_data:
            # Update access metadata
            cached_data["metadata"]["hits"] = cached_data["metadata"].get("hits", 0) + 1
            cached_data["metadata"]["last_accessed"] = self.cache_manager._stats["hits"]
            await self.cache_manager.set(f"llm:{key}", cached_data, ttl=cached_data.get("ttl"))
            return cached_data["response"]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set LLM response in cache."""
        import time

        cache_entry = {
            "response": value,
            "ttl": ttl or self.cache_manager.config.default_ttl,
            "created_at": time.time(),
            "metadata": {
                "hits": 0,
                "model": value.get("model", "unknown"),
                "tokens_used": value.get("usage", {}).get("total_tokens", 0),
            }
        }
        await self.cache_manager.set(f"llm:{key}", cache_entry, ttl=ttl)

    def generate_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key for LLM requests."""
        # Normalize the prompt (remove extra whitespace)
        normalized_prompt = " ".join(prompt.split())

        # Include relevant parameters in key
        key_components = [
            normalized_prompt,
            model,
            kwargs.get("temperature", 1.0),
            kwargs.get("max_tokens", "none"),
            kwargs.get("system_prompt", ""),
        ]

        key_string = "|".join(str(component) for component in key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()


class VectorCacheStrategy(BaseCacheStrategy):
    """Cache strategy for vector search results."""

    async def get(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Get vector search results from cache."""
        cached_data = await self.cache_manager.get(f"vector:{key}")
        if cached_data:
            return cached_data["results"]
        return None

    async def set(self, key: str, value: List[Dict[str, Any]], ttl: Optional[int] = None) -> None:
        """Set vector search results in cache."""
        import time

        cache_entry = {
            "results": value,
            "ttl": ttl or self.cache_manager.config.default_ttl,
            "created_at": time.time(),
            "metadata": {
                "result_count": len(value),
                "query_type": "vector_search"
            }
        }
        await self.cache_manager.set(f"vector:{key}", cache_entry, ttl=ttl)

    def generate_key(self, query: str, top_k: int = 5, **kwargs) -> str:
        """Generate cache key for vector search."""
        key_components = [
            query.strip().lower(),
            str(top_k),
            kwargs.get("filter", ""),
            kwargs.get("namespace", "default"),
        ]
        key_string = "|".join(key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()


class AgentResultCacheStrategy(BaseCacheStrategy):
    """Cache strategy for agent execution results."""

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get agent result from cache."""
        cached_data = await self.cache_manager.get(f"agent:{key}")
        if cached_data:
            return cached_data["result"]
        return None

    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set agent result in cache."""
        import time

        cache_entry = {
            "result": value,
            "ttl": ttl or self.cache_manager.config.default_ttl,
            "created_at": time.time(),
            "metadata": {
                "agent_name": value.get("metadata", {}).get("agent_name", "unknown"),
                "success": value.get("success", False),
                "execution_time": value.get("execution_time", 0),
            }
        }
        await self.cache_manager.set(f"agent:{key}", cache_entry, ttl=ttl)

    def generate_key(self, agent_name: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key for agent execution."""
        # Sort input data for consistent hashing
        sorted_input = json.dumps(input_data, sort_keys=True)
        key_components = [agent_name, sorted_input]
        key_string = "|".join(key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()


class SemanticCacheStrategy(BaseCacheStrategy):
    """Semantic caching using embeddings for similarity matching."""

    def __init__(self, cache_manager: CacheManager):
        super().__init__(cache_manager)
        self.embedding_cache: Dict[str, List[float]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get semantically similar result from cache."""
        # First try exact match
        exact_match = await self.cache_manager.get(f"semantic:{key}")
        if exact_match:
            return exact_match

        # Try semantic similarity
        query_embedding = await self._get_embedding(key)
        if not query_embedding:
            return None

        # Find similar cached queries
        similar_key = await self._find_similar_query(query_embedding)
        if similar_key:
            return await self.cache_manager.get(f"semantic:{similar_key}")

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value with semantic caching."""
        await self.cache_manager.set(f"semantic:{key}", value, ttl=ttl)

        # Cache the embedding
        embedding = await self._get_embedding(key)
        if embedding:
            self.embedding_cache[key] = embedding

    def generate_key(self, text: str) -> str:
        """Generate cache key for semantic search."""
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text (simplified implementation)."""
        # In a real implementation, this would use an embedding model
        # For now, return a simple hash-based "embedding"
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        # Generate a deterministic "embedding" based on text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to list of floats (simplified)
        embedding = [float(b) / 255.0 for b in hash_bytes[:128]]  # First 128 bytes
        self.embedding_cache[text] = embedding
        return embedding

    async def _find_similar_query(self, query_embedding: List[float]) -> Optional[str]:
        """Find semantically similar cached query."""
        max_similarity = 0.0
        most_similar_key = None

        for cached_key, cached_embedding in self.embedding_cache.items():
            similarity = self._cosine_similarity(query_embedding, cached_embedding)
            if similarity > max_similarity and similarity >= self.cache_manager.config.semantic_similarity_threshold:
                max_similarity = similarity
                most_similar_key = cached_key

        return most_similar_key

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)
