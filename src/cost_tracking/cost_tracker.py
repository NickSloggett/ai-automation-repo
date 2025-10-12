"""Cost tracking implementation."""

import asyncio
import time
from collections import defaultdict
from typing import Dict, List, Optional, Any
import json

import structlog

from ..caching import get_cache_manager
from ..config import get_settings
from .models import CostRecord, CostSummary, CostAlert
from .pricing import get_model_pricing

logger = structlog.get_logger(__name__)


class CostTracker:
    """Tracks and monitors LLM API costs."""

    def __init__(self):
        self.settings = get_settings()
        self.cache_manager = None
        self._cost_records: List[CostRecord] = []
        self._alerts: List[CostAlert] = []
        self._budget_limits: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the cost tracker."""
        self.cache_manager = await get_cache_manager()

        # Load existing cost records from cache/persistence
        await self._load_cost_records()

    async def track_cost(
        self,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: Optional[float] = None,
        **kwargs
    ) -> CostRecord:
        """Track a cost event."""
        async with self._lock:
            # Get pricing
            pricing = get_model_pricing(model)
            cost = 0.0

            if pricing:
                cost = pricing.calculate_cost(input_tokens, output_tokens)
            else:
                logger.warning("No pricing available for model", model=model)

            # Create cost record
            record = CostRecord.create(
                model=model,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                latency_ms=latency_ms,
                **kwargs
            )

            # Store record
            self._cost_records.append(record)
            await self._persist_record(record)

            # Check budget limits
            await self._check_budget_limits(record)

            logger.info(
                "Cost tracked",
                model=model,
                cost=cost,
                total_tokens=record.total_tokens,
                agent_name=kwargs.get("agent_name")
            )

            return record

    async def get_cost_summary(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> CostSummary:
        """Get cost summary for a time period."""
        if start_time is None:
            start_time = time.time() - (24 * 60 * 60)  # Last 24 hours
        if end_time is None:
            end_time = time.time()

        # Filter records
        filtered_records = [
            record for record in self._cost_records
            if start_time <= record.timestamp <= end_time
            and (agent_name is None or record.agent_name == agent_name)
            and (user_id is None or record.user_id == user_id)
        ]

        # Calculate summary
        total_cost = sum(record.cost for record in filtered_records)
        total_tokens = sum(record.total_tokens for record in filtered_records)
        total_requests = len(filtered_records)

        # Model breakdown
        model_breakdown = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "requests": 0})
        for record in filtered_records:
            model_breakdown[record.model]["cost"] += record.cost
            model_breakdown[record.model]["tokens"] += record.total_tokens
            model_breakdown[record.model]["requests"] += 1

        # Agent breakdown
        agent_breakdown = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "requests": 0})
        for record in filtered_records:
            agent_name = record.agent_name or "unknown"
            agent_breakdown[agent_name]["cost"] += record.cost
            agent_breakdown[agent_name]["tokens"] += record.total_tokens
            agent_breakdown[agent_name]["requests"] += 1

        # Provider breakdown
        provider_breakdown = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "requests": 0})
        for record in filtered_records:
            provider_breakdown[record.provider]["cost"] += record.cost
            provider_breakdown[record.provider]["tokens"] += record.total_tokens
            provider_breakdown[record.provider]["requests"] += 1

        # Performance metrics
        latencies = [r.latency_ms for r in filtered_records if r.latency_ms is not None]
        average_latency = sum(latencies) / len(latencies) if latencies else None

        cache_hits = sum(1 for r in filtered_records if r.cache_hit)
        cache_hit_rate = cache_hits / total_requests if total_requests > 0 else None

        # Budget information
        budget_limit = self._budget_limits.get("global")
        budget_used_percent = None
        if budget_limit:
            budget_used_percent = (total_cost / budget_limit) * 100

        return CostSummary(
            period_start=start_time,
            period_end=end_time,
            total_cost=total_cost,
            total_tokens=total_tokens,
            total_requests=total_requests,
            model_breakdown=dict(model_breakdown),
            agent_breakdown=dict(agent_breakdown),
            provider_breakdown=dict(provider_breakdown),
            average_latency_ms=average_latency,
            cache_hit_rate=cache_hit_rate,
            budget_limit=budget_limit,
            budget_used_percent=budget_used_percent,
        )

    async def set_budget_limit(self, category: str, limit: float) -> None:
        """Set budget limit for a category."""
        self._budget_limits[category] = limit
        logger.info("Budget limit set", category=category, limit=limit)

    async def get_alerts(self, since: Optional[float] = None) -> List[CostAlert]:
        """Get cost alerts."""
        if since is None:
            since = time.time() - (24 * 60 * 60)  # Last 24 hours

        return [alert for alert in self._alerts if alert.timestamp >= since]

    async def _check_budget_limits(self, record: CostRecord) -> None:
        """Check if any budget limits have been exceeded."""
        # Check global budget
        if "global" in self._budget_limits:
            summary = await self.get_cost_summary(
                start_time=time.time() - (30 * 24 * 60 * 60)  # Last 30 days
            )
            if summary.budget_used_percent and summary.budget_used_percent >= 100:
                alert = CostAlert(
                    alert_type="budget_limit",
                    message=f"Global budget limit exceeded: ${summary.total_cost:.2f} used of ${self._budget_limits['global']:.2f}",
                    threshold_value=self._budget_limits["global"],
                    current_value=summary.total_cost,
                    timestamp=time.time(),
                    metadata={"category": "global"}
                )
                self._alerts.append(alert)
                logger.warning("Budget limit exceeded", alert=alert.dict())

    async def _persist_record(self, record: CostRecord) -> None:
        """Persist cost record to storage."""
        if self.cache_manager:
            # Store in cache with TTL (keep for 90 days)
            await self.cache_manager.set(
                f"cost_record:{record.id}",
                record.dict(),
                ttl=90 * 24 * 60 * 60
            )

            # Also maintain a list of recent records
            await self._update_cost_record_list(record)

    async def _load_cost_records(self) -> None:
        """Load cost records from storage."""
        # This is a simplified implementation
        # In production, you might want to load from database
        pass

    async def _update_cost_record_list(self, record: CostRecord) -> None:
        """Update the list of cost records in cache."""
        # Get existing list
        cache_key = "cost_records_list"
        record_list = await self.cache_manager.get(cache_key) or []

        # Add new record
        record_list.append(record.id)

        # Keep only last 10000 records to prevent unbounded growth
        if len(record_list) > 10000:
            # Remove oldest records
            records_to_remove = record_list[:-10000]
            record_list = record_list[-10000:]

            # Clean up old records
            for old_id in records_to_remove:
                await self.cache_manager.delete(f"cost_record:{old_id}")

        # Save updated list
        await self.cache_manager.set(cache_key, record_list, ttl=90 * 24 * 60 * 60)


# Global cost tracker instance
_cost_tracker: Optional[CostTracker] = None


async def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
        await _cost_tracker.initialize()
    return _cost_tracker


async def track_llm_cost(
    model: str,
    provider: str,
    input_tokens: int,
    output_tokens: int,
    **kwargs
) -> None:
    """Convenience function to track LLM costs."""
    tracker = await get_cost_tracker()
    await tracker.track_cost(
        model=model,
        provider=provider,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        **kwargs
    )
