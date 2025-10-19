"""LLM pricing information and cost calculations."""

from typing import Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class ModelPricing:
    """Pricing information for LLM models."""

    def __init__(
        self,
        model_name: str,
        input_token_cost: float,  # Cost per 1K input tokens
        output_token_cost: float,  # Cost per 1K output tokens
        currency: str = "USD",
    ):
        self.model_name = model_name
        self.input_token_cost = input_token_cost
        self.output_token_cost = output_token_cost
        self.currency = currency

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage."""
        input_cost = (input_tokens / 1000) * self.input_token_cost
        output_cost = (output_tokens / 1000) * self.output_token_cost
        return input_cost + output_cost


# Pricing data (as of 2024 - should be updated regularly)
MODEL_PRICING = {
    # OpenAI models
    "gpt-4": ModelPricing("gpt-4", 0.03, 0.06),
    "gpt-4-turbo": ModelPricing("gpt-4-turbo", 0.01, 0.03),
    "gpt-4-turbo-preview": ModelPricing("gpt-4-turbo-preview", 0.01, 0.03),
    "gpt-3.5-turbo": ModelPricing("gpt-3.5-turbo", 0.0015, 0.002),
    "gpt-3.5-turbo-16k": ModelPricing("gpt-3.5-turbo-16k", 0.003, 0.004),

    # Anthropic models
    "claude-3-opus": ModelPricing("claude-3-opus", 0.015, 0.075),
    "claude-3-sonnet": ModelPricing("claude-3-sonnet", 0.003, 0.015),
    "claude-3-haiku": ModelPricing("claude-3-haiku", 0.00025, 0.00125),
    "claude-2": ModelPricing("claude-2", 0.008, 0.024),

    # Groq models (Llama)
    "llama2-70b-4096": ModelPricing("llama2-70b-4096", 0.0007, 0.0007),
    "llama2-13b-4096": ModelPricing("llama2-13b-4096", 0.00035, 0.00035),
    "mixtral-8x7b-32768": ModelPricing("mixtral-8x7b-32768", 0.00027, 0.00027),
}


def get_model_pricing(model_name: str) -> Optional[ModelPricing]:
    """Get pricing information for a model."""
    # Try exact match first
    if model_name in MODEL_PRICING:
        return MODEL_PRICING[model_name]

    # Try partial match for model families
    for pricing_model, pricing in MODEL_PRICING.items():
        if pricing_model in model_name or model_name in pricing_model:
            return pricing

    logger.warning("No pricing found for model", model_name=model_name)
    return None


def update_model_pricing(model_name: str, input_cost: float, output_cost: float) -> None:
    """Update pricing for a model."""
    MODEL_PRICING[model_name] = ModelPricing(model_name, input_cost, output_cost)
    logger.info("Updated model pricing", model_name=model_name)


def get_all_model_pricing() -> Dict[str, ModelPricing]:
    """Get all model pricing information."""
    return MODEL_PRICING.copy()

