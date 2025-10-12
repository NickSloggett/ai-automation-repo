"""Circuit breaker implementation for resilient API calls."""

import asyncio
import time
from typing import Any, Callable, Dict, Optional, Union

import structlog

from ..caching import get_cache_manager
from .states import CircuitBreakerState

logger = structlog.get_logger(__name__)


class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: tuple = (Exception,),
        success_threshold: int = 3,
        timeout: float = 30.0,
        name: str = "default",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.name = name


class CircuitBreaker:
    """Circuit breaker for resilient API calls."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._call_count = 0
        self._cache_manager = None

    @property
    def state(self) -> CircuitBreakerState:
        """Get current state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get failure count."""
        return self._failure_count

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self._state == CircuitBreakerState.OPEN:
            if not self._should_attempt_reset():
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.config.name}' is OPEN"
                )
            self._state = CircuitBreakerState.HALF_OPEN
            logger.info(
                "Circuit breaker transitioning to HALF_OPEN",
                name=self.config.name
            )

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )

            self._on_success()
            return result

        except self.config.expected_exception as e:
            self._on_failure()
            raise
        except asyncio.TimeoutError as e:
            self._on_failure()
            raise CircuitBreakerTimeoutException(
                f"Call timed out after {self.config.timeout}s"
            ) from e

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker."""
        if self._last_failure_time is None:
            return False

        return (time.time() - self._last_failure_time) >= self.config.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful call."""
        self._call_count += 1

        if self._state == CircuitBreakerState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._reset()
        else:
            # Reset failure count on success in CLOSED state
            self._failure_count = max(0, self._failure_count - 1)

    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        self._call_count += 1

        if self._failure_count >= self.config.failure_threshold:
            self._trip()

    def _trip(self) -> None:
        """Trip the circuit breaker to OPEN state."""
        self._state = CircuitBreakerState.OPEN
        logger.warning(
            "Circuit breaker tripped to OPEN",
            name=self.config.name,
            failure_count=self._failure_count
        )

    def _reset(self) -> None:
        """Reset the circuit breaker to CLOSED state."""
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        logger.info(
            "Circuit breaker reset to CLOSED",
            name=self.config.name
        )

    async def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.config.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "call_count": self._call_count,
            "last_failure_time": self._last_failure_time,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
            }
        }


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerTimeoutException(Exception):
    """Exception raised when circuit breaker times out."""
    pass


# Global circuit breaker registry
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """Get or create a circuit breaker instance."""
    if name not in _circuit_breakers:
        if config is None:
            config = CircuitBreakerConfig(name=name)
        _circuit_breakers[name] = CircuitBreaker(config)

    return _circuit_breakers[name]


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: tuple = (Exception,),
    success_threshold: int = 3,
    timeout: float = 30.0,
    name: Optional[str] = None,
):
    """Decorator for circuit breaker pattern."""
    def decorator(func: Callable):
        circuit_name = name or f"{func.__module__}.{func.__name__}"
        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            success_threshold=success_threshold,
            timeout=timeout,
            name=circuit_name,
        )
        cb = get_circuit_breaker(circuit_name, config)

        async def wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)

        return wrapper

    return decorator


async def get_circuit_breaker_stats() -> Dict[str, Any]:
    """Get statistics for all circuit breakers."""
    stats = {}
    for name, cb in _circuit_breakers.items():
        stats[name] = await cb.get_stats()
    return stats
