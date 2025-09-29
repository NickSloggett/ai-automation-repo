"""Decision-making agent for AI automation workflows."""

from typing import Any, Dict, List, Optional

import structlog
from pydantic import BaseModel

from .base import AgentConfig, AgentResult, BaseAgent

logger = structlog.get_logger(__name__)


class DecisionConfig(AgentConfig):
    """Configuration specific to decision agents."""

    decision_criteria: List[str] = []
    confidence_threshold: float = 0.7
    alternatives: List[str] = []
    reasoning_steps: int = 3


class DecisionOption(BaseModel):
    """A decision option with reasoning."""

    option: str
    confidence: float
    reasoning: str
    pros: List[str] = []
    cons: List[str] = []
    metadata: Dict[str, Any] = {}


class DecisionResult(BaseModel):
    """Result from a decision-making process."""

    chosen_option: str
    confidence: float
    reasoning: str
    alternatives: List[DecisionOption] = []
    criteria_met: Dict[str, bool] = {}


class DecisionAgent(BaseAgent):
    """Agent for making intelligent decisions based on criteria and context."""

    def __init__(self, config: DecisionConfig):
        """Initialize the decision agent.

        Args:
            config: Decision configuration
        """
        super().__init__(config)
        self.decision_config = config
        self.logger = logger.bind(agent_type="decision")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Make a decision based on input criteria and context.

        Args:
            input_data: Input data containing decision context and criteria

        Returns:
            Decision result
        """
        try:
            # Validate input
            if not self.validate_input(input_data):
                return AgentResult(
                    success=False,
                    error="Invalid input data for decision making",
                    metadata={"agent_name": self.config.name}
                )

            # Gather context and criteria
            context = await self._gather_context(input_data)
            criteria = await self._evaluate_criteria(input_data)

            # Generate decision options
            options = await self._generate_options(context, criteria)

            # Evaluate options
            evaluated_options = await self._evaluate_options(options, context, criteria)

            # Select best option
            best_option = await self._select_best_option(evaluated_options)

            # Validate decision
            validation_result = await self._validate_decision(best_option, context, criteria)
            if not validation_result.success:
                return AgentResult(
                    success=False,
                    error=f"Decision validation failed: {validation_result.error}",
                    metadata={"agent_name": self.config.name}
                )

            return AgentResult(
                success=True,
                data={
                    "decision": best_option.dict(),
                    "context": context,
                    "criteria": criteria,
                    "all_options": [opt.dict() for opt in evaluated_options]
                },
                metadata={"agent_name": self.config.name}
            )

        except Exception as e:
            self.logger.error("Decision making failed", error=str(e), exc_info=True)
            return AgentResult(
                success=False,
                error=f"Decision making failed: {str(e)}",
                metadata={"agent_name": self.config.name}
            )

    async def _gather_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gather relevant context for the decision.

        Args:
            input_data: Input data containing context

        Returns:
            Context dictionary
        """
        # Extract context from input data
        context = {
            "situation": input_data.get("situation", ""),
            "constraints": input_data.get("constraints", []),
            "goals": input_data.get("goals", []),
            "risk_tolerance": input_data.get("risk_tolerance", "medium"),
            "timeframe": input_data.get("timeframe", "medium"),
        }

        # Add any additional context from external sources
        additional_context = await self._get_additional_context(input_data)
        context.update(additional_context)

        return context

    async def _evaluate_criteria(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the decision criteria.

        Args:
            input_data: Input data containing criteria

        Returns:
            Criteria evaluation results
        """
        criteria_results = {}

        for criterion in self.decision_config.decision_criteria:
            # Evaluate each criterion based on input data
            evaluation = await self._evaluate_criterion(criterion, input_data)
            criteria_results[criterion] = evaluation

        return criteria_results

    async def _generate_options(self, context: Dict[str, Any], criteria: Dict[str, Any]) -> List[str]:
        """Generate possible decision options.

        Args:
            context: Decision context
            criteria: Evaluated criteria

        Returns:
            List of possible options
        """
        # Start with configured alternatives
        options = self.decision_config.alternatives.copy()

        # Generate additional options based on context
        additional_options = await self._generate_additional_options(context, criteria)
        options.extend(additional_options)

        # Remove duplicates
        options = list(set(options))

        return options

    async def _evaluate_options(
        self,
        options: List[str],
        context: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> List[DecisionOption]:
        """Evaluate each decision option.

        Args:
            options: List of options to evaluate
            context: Decision context
            criteria: Evaluated criteria

        Returns:
            List of evaluated options with reasoning
        """
        evaluated_options = []

        for option in options:
            evaluation = await self._evaluate_single_option(option, context, criteria)
            evaluated_options.append(evaluation)

        # Sort by confidence
        evaluated_options.sort(key=lambda x: x.confidence, reverse=True)

        return evaluated_options

    async def _evaluate_single_option(
        self,
        option: str,
        context: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> DecisionOption:
        """Evaluate a single decision option.

        Args:
            option: Option to evaluate
            context: Decision context
            criteria: Evaluated criteria

        Returns:
            Evaluated option with reasoning
        """
        # Calculate confidence based on criteria
        confidence = await self._calculate_confidence(option, context, criteria)

        # Generate reasoning
        reasoning = await self._generate_reasoning(option, context, criteria, confidence)

        # Identify pros and cons
        pros, cons = await self._identify_pros_cons(option, context, criteria)

        return DecisionOption(
            option=option,
            confidence=confidence,
            reasoning=reasoning,
            pros=pros,
            cons=cons,
            metadata={"criteria_scores": criteria}
        )

    async def _select_best_option(self, evaluated_options: List[DecisionOption]) -> DecisionOption:
        """Select the best option from evaluated options.

        Args:
            evaluated_options: List of evaluated options

        Returns:
            Best option
        """
        if not evaluated_options:
            raise ValueError("No options available for selection")

        # Filter options that meet minimum confidence threshold
        viable_options = [
            opt for opt in evaluated_options
            if opt.confidence >= self.decision_config.confidence_threshold
        ]

        if not viable_options:
            # If no options meet threshold, return highest confidence option
            self.logger.warning(
                "No options meet confidence threshold, selecting highest confidence",
                threshold=self.decision_config.confidence_threshold,
                max_confidence=evaluated_options[0].confidence
            )
            return evaluated_options[0]

        return viable_options[0]

    async def _validate_decision(
        self,
        decision: DecisionOption,
        context: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> AgentResult:
        """Validate the final decision.

        Args:
            decision: Selected decision option
            context: Decision context
            criteria: Evaluated criteria

        Returns:
            Validation result
        """
        # Check if decision meets all critical criteria
        critical_criteria = await self._get_critical_criteria(context)
        criteria_met = {}

        for criterion in critical_criteria:
            met = criteria.get(criterion, {}).get("met", False)
            criteria_met[criterion] = met

            if not met:
                return AgentResult(
                    success=False,
                    error=f"Decision fails critical criterion: {criterion}",
                    data={"criteria_met": criteria_met}
                )

        return AgentResult(
            success=True,
            data=DecisionResult(
                chosen_option=decision.option,
                confidence=decision.confidence,
                reasoning=decision.reasoning,
                alternatives=evaluated_options[1:],  # All except the chosen one
                criteria_met=criteria_met
            )
        )

    # Helper methods to be implemented by subclasses or with specific logic

    async def _get_additional_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get additional context from external sources."""
        return {}

    async def _evaluate_criterion(self, criterion: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a specific criterion."""
        return {"met": True, "score": 0.8, "reasoning": "Criterion evaluation"}

    async def _generate_additional_options(self, context: Dict[str, Any], criteria: Dict[str, Any]) -> List[str]:
        """Generate additional decision options."""
        return []

    async def _calculate_confidence(self, option: str, context: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate confidence score for an option."""
        # Simple confidence calculation - can be enhanced with ML models
        base_confidence = 0.5
        criteria_bonus = sum(criteria.values()) / len(criteria) if criteria else 0
        return min(base_confidence + criteria_bonus * 0.3, 1.0)

    async def _generate_reasoning(self, option: str, context: Dict[str, Any], criteria: Dict[str, Any], confidence: float) -> str:
        """Generate reasoning for an option."""
        return f"Option '{option}' was selected with {confidence".2f"} confidence based on the given criteria."

    async def _identify_pros_cons(self, option: str, context: Dict[str, Any], criteria: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Identify pros and cons for an option."""
        return ["Pro 1", "Pro 2"], ["Con 1", "Con 2"]

    async def _get_critical_criteria(self, context: Dict[str, Any]) -> List[str]:
        """Get list of critical criteria that must be met."""
        return self.decision_config.decision_criteria

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for decision making.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid, False otherwise
        """
        required_fields = ["situation"]
        for field in required_fields:
            if field not in input_data:
                self.logger.error("Missing required input field", field=field)
                return False

        return True
