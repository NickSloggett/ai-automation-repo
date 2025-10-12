"""Cache manager for handling different caching strategies."""

import asyncio
import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import redis.asyncio as redis
from aiocache import Cache, cached
from pydantic import BaseModel

from ..config import get_settings


class CacheConfig(BaseModel):
    """Configuration for cache manager."""

    redis_url: str = "redis://localhost:6379/0"
    default_ttl: int = 3600  # 1 hour
    max_memory_mb: int = 512
    enable_compression: bool = True
    semantic_similarity_threshold: float = 0.85


class CacheEntry(BaseModel):
    """Cache entry with metadata."""

    key: str
    value: Any
    ttl: int
    created_at: float
    hits: int = 0
    last_accessed: float = 0.0
    metadata: Dict[str, Any] = {}


class BaseCacheStrategy(ABC):
    """Base class for cache strategies."""

    def __init__(self, cache_manager: "CacheManager"):
        self.cache_manager = cache_manager

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass

    @abstractmethod
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key."""
        pass


class CacheManager:
    """Central cache manager with multiple strategies."""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.settings = get_settings()
        self._redis: Optional[redis.Redis] = None
        self._local_cache = Cache()
        self._strategies: Dict[str, BaseCacheStrategy] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
        }

    async def initialize(self) -> None:
        """Initialize cache connections."""
        try:
            self._redis = redis.Redis.from_url(
                self.config.redis_url,
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
            )
            await self._redis.ping()
        except Exception:
            # Fallback to local cache only
            self._redis = None

    async def close(self) -> None:
        """Close cache connections."""
        if self._redis:
            await self._redis.close()

    def register_strategy(self, name: str, strategy: BaseCacheStrategy) -> None:
        """Register a cache strategy."""
        self._strategies[name] = strategy

    def get_strategy(self, name: str) -> Optional[BaseCacheStrategy]:
        """Get a registered cache strategy."""
        return self._strategies.get(name)

    async def get(self, key: str, strategy: str = "default") -> Optional[Any]:
        """Get value from cache using specified strategy."""
        cache_strategy = self.get_strategy(strategy)
        if cache_strategy:
            return await cache_strategy.get(key)

        # Default strategy
        return await self._get_default(key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        strategy: str = "default"
    ) -> None:
        """Set value in cache using specified strategy."""
        cache_strategy = self.get_strategy(strategy)
        if cache_strategy:
            await cache_strategy.set(key, value, ttl)
            return

        # Default strategy
        await self._set_default(key, value, ttl)

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        if self._redis:
            await self._redis.delete(key)
        await self._local_cache.delete(key)

    async def clear(self) -> None:
        """Clear all cache entries."""
        if self._redis:
            await self._redis.flushdb()
        await self._local_cache.clear()

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if self._redis:
            redis_exists = await self._redis.exists(key)
            if redis_exists:
                return True
        return await self._local_cache.exists(key)

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        redis_info = {}
        if self._redis:
            try:
                redis_info = await self._redis.info()
            except Exception:
                redis_info = {"error": "Unable to get Redis info"}

        return {
            "cache_stats": self._stats,
            "redis_info": redis_info,
            "local_cache_size": len(await self._local_cache.keys()),
            "config": self.config.dict(),
        }

    async def _get_default(self, key: str) -> Optional[Any]:
        """Default cache get implementation."""
        # Try Redis first
        if self._redis:
            try:
                data = await self._redis.get(key)
                if data:
                    self._stats["hits"] += 1
                    return json.loads(data)
            except Exception:
                pass

        # Fallback to local cache
        try:
            value = await self._local_cache.get(key)
            if value is not None:
                self._stats["hits"] += 1
                return value
        except Exception:
            pass

        self._stats["misses"] += 1
        return None

    async def _set_default(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Default cache set implementation."""
        ttl = ttl or self.config.default_ttl
        serialized_value = json.dumps(value, default=str)

        # Set in Redis
        if self._redis:
            try:
                await self._redis.setex(key, ttl, serialized_value)
            except Exception:
                pass

        # Also set in local cache
        await self._local_cache.set(key, value, ttl=ttl)
        self._stats["sets"] += 1

    def generate_key(self, *args, **kwargs) -> str:
        """Generate a deterministic cache key."""
        # Sort kwargs for consistency
        sorted_kwargs = sorted(kwargs.items())
        key_components = list(args) + [f"{k}:{v}" for k, v in sorted_kwargs]

        # Create hash of the key components
        key_string = "|".join(str(component) for component in key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()
    return _cache_manager


async def close_cache_manager() -> None:
    """Close the global cache manager."""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None
