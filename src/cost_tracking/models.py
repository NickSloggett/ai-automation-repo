"""Data models for cost tracking."""

import time
from typing import Dict, Any, Optional
from pydantic import BaseModel


class CostRecord(BaseModel):
    """Record of a single API call cost."""

    id: str
    timestamp: float
    model: str
    provider: str
    agent_name: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Token usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    # Cost
    cost: float = 0.0
    currency: str = "USD"

    # Metadata
    endpoint: Optional[str] = None
    request_id: Optional[str] = None
    error: Optional[str] = None
    cache_hit: bool = False

    # Performance
    latency_ms: Optional[float] = None

    @classmethod
    def create(
        cls,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        **kwargs
    ) -> "CostRecord":
        """Create a new cost record."""
        import uuid

        return cls(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=cost,
            **kwargs
        )


class CostSummary(BaseModel):
    """Summary of costs over a time period."""

    period_start: float
    period_end: float
    total_cost: float
    total_tokens: int
    total_requests: int
    currency: str = "USD"

    # Breakdown by model
    model_breakdown: Dict[str, Dict[str, Any]] = {}

    # Breakdown by agent
    agent_breakdown: Dict[str, Dict[str, Any]] = {}

    # Breakdown by provider
    provider_breakdown: Dict[str, Dict[str, Any]] = {}

    # Performance metrics
    average_latency_ms: Optional[float] = None
    cache_hit_rate: Optional[float] = None

    # Budget information
    budget_limit: Optional[float] = None
    budget_used_percent: Optional[float] = None


class CostAlert(BaseModel):
    """Alert for cost thresholds."""

    alert_type: str  # "budget_limit", "spike", "anomaly"
    message: str
    threshold_value: float
    current_value: float
    timestamp: float
    metadata: Dict[str, Any] = {}
