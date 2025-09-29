"""Monitoring and metrics utilities."""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

import structlog
from prometheus_client import Counter, Histogram, start_http_server

from ..config import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('ai_automation_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('ai_automation_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
AGENT_EXECUTIONS = Counter('ai_automation_agent_executions_total', 'Agent executions', ['agent_name', 'status'])
TASK_DURATION = Histogram('ai_automation_task_duration_seconds', 'Task duration', ['task_type'])


def init_monitoring() -> None:
    """Initialize monitoring and metrics collection."""
    if settings.monitoring.enable_metrics:
        try:
            start_http_server(settings.monitoring.metrics_port)
            logger.info("Metrics server started", port=settings.monitoring.metrics_port)
        except Exception as e:
            logger.error("Failed to start metrics server", error=str(e))


def track_performance(func: Callable) -> Callable:
    """Decorator to track function performance metrics.

    Args:
        func: Function to track

    Returns:
        Wrapped function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Track successful execution
            if hasattr(func, '__name__'):
                TASK_DURATION.labels(task_type=func.__name__).observe(execution_time)

            logger.info(
                "Function executed successfully",
                function_name=func.__name__,
                execution_time=execution_time
            )

            return result

        except Exception as e:
            execution_time = time.time() - start_time

            logger.error(
                "Function execution failed",
                function_name=func.__name__,
                execution_time=execution_time,
                error=str(e)
            )
            raise

    return wrapper


def track_agent_execution(agent_name: str, success: bool) -> None:
    """Track agent execution metrics.

    Args:
        agent_name: Name of the agent
        success: Whether execution was successful
    """
    status = "success" if success else "failure"
    AGENT_EXECUTIONS.labels(agent_name=agent_name, status=status).inc()

    logger.info(
        "Agent execution tracked",
        agent_name=agent_name,
        success=success,
        status=status
    )


def track_request(method: str, endpoint: str, duration: float, status_code: int = 200) -> None:
    """Track API request metrics.

    Args:
        method: HTTP method
        endpoint: Request endpoint
        duration: Request duration in seconds
        status_code: HTTP status code
    """
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    logger.debug(
        "Request tracked",
        method=method,
        endpoint=endpoint,
        duration=duration,
        status_code=status_code
    )
