"""Agent testing framework."""

import asyncio
import time
from typing import Any, Dict, List, Optional, Callable
import pytest

from ..agents.base import BaseAgent, AgentConfig, AgentResult
from .llm_mocker import LLMMocker


class TestScenario:
    """Test scenario for agent testing."""

    def __init__(
        self,
        name: str,
        input_data: Dict[str, Any],
        expected_output: Optional[Any] = None,
        expected_success: bool = True,
        expected_error: Optional[str] = None,
        timeout: Optional[float] = None,
        setup_func: Optional[Callable] = None,
        teardown_func: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.input_data = input_data
        self.expected_output = expected_output
        self.expected_success = expected_success
        self.expected_error = expected_error
        self.timeout = timeout
        self.setup_func = setup_func
        self.teardown_func = teardown_func
        self.metadata = metadata or {}


class TestResult:
    """Result of an agent test."""

    def __init__(
        self,
        scenario: TestScenario,
        result: AgentResult,
        execution_time: float,
        passed: bool,
        failure_reason: Optional[str] = None,
    ):
        self.scenario = scenario
        self.result = result
        self.execution_time = execution_time
        self.passed = passed
        self.failure_reason = failure_reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_name": self.scenario.name,
            "passed": self.passed,
            "execution_time": self.execution_time,
            "failure_reason": self.failure_reason,
            "result": self.result.dict() if self.result else None,
            "expected_success": self.scenario.expected_success,
            "expected_error": self.scenario.expected_error,
        }


class AgentTester:
    """Test runner for agents."""

    def __init__(self, agent_class: type, agent_config: Optional[AgentConfig] = None):
        self.agent_class = agent_class
        self.agent_config = agent_config or AgentConfig(name="test_agent")
        self.llm_mocker = LLMMocker()
        self.test_scenarios: List[TestScenario] = []
        self.test_results: List[TestResult] = []

    def add_scenario(self, scenario: TestScenario) -> None:
        """Add a test scenario."""
        self.test_scenarios.append(scenario)

    def add_simple_scenario(
        self,
        name: str,
        input_data: Dict[str, Any],
        expected_output: Optional[Any] = None,
        **kwargs
    ) -> None:
        """Add a simple test scenario."""
        scenario = TestScenario(
            name=name,
            input_data=input_data,
            expected_output=expected_output,
            **kwargs
        )
        self.add_scenario(scenario)

    def setup_llm_mock(self) -> None:
        """Setup LLM mocking for the agent."""
        # This would typically monkey-patch the LLM provider
        # For now, we'll assume the agent accepts an llm_provider parameter
        pass

    async def run_test_scenario(self, scenario: TestScenario) -> TestResult:
        """Run a single test scenario."""
        start_time = time.time()

        try:
            # Setup
            if scenario.setup_func:
                await scenario.setup_func()

            # Create agent instance
            agent = self.agent_class(self.agent_config)

            # Run agent
            timeout = scenario.timeout or 30.0
            result = await asyncio.wait_for(
                agent.run(scenario.input_data),
                timeout=timeout
            )

            execution_time = time.time() - start_time

            # Validate result
            passed = self._validate_result(scenario, result)
            failure_reason = None if passed else self._get_failure_reason(scenario, result)

            test_result = TestResult(
                scenario=scenario,
                result=result,
                execution_time=execution_time,
                passed=passed,
                failure_reason=failure_reason,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_result = AgentResult(
                success=False,
                error=f"Test execution failed: {str(e)}",
                execution_time=execution_time,
            )

            test_result = TestResult(
                scenario=scenario,
                result=error_result,
                execution_time=execution_time,
                passed=False,
                failure_reason=f"Exception during test: {str(e)}",
            )

        finally:
            # Teardown
            if scenario.teardown_func:
                try:
                    await scenario.teardown_func()
                except Exception as e:
                    print(f"Teardown failed: {e}")

        return test_result

    async def run_all_tests(self) -> List[TestResult]:
        """Run all test scenarios."""
        self.test_results.clear()

        for scenario in self.test_scenarios:
            result = await self.run_test_scenario(scenario)
            self.test_results.append(result)

        return self.test_results

    def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests

        total_execution_time = sum(result.execution_time for result in self.test_results)
        average_execution_time = total_execution_time / total_tests if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_execution_time": total_execution_time,
            "average_execution_time": average_execution_time,
        }

    def get_failed_tests(self) -> List[TestResult]:
        """Get failed test results."""
        return [result for result in self.test_results if not result.passed]

    def _validate_result(self, scenario: TestScenario, result: AgentResult) -> bool:
        """Validate test result against scenario expectations."""
        # Check success/failure
        if result.success != scenario.expected_success:
            return False

        # Check error message
        if scenario.expected_error:
            if not result.error or scenario.expected_error not in result.error:
                return False

        # Check output
        if scenario.expected_output is not None:
            if result.data != scenario.expected_output:
                return False

        return True

    def _get_failure_reason(self, scenario: TestScenario, result: AgentResult) -> str:
        """Get detailed failure reason."""
        reasons = []

        if result.success != scenario.expected_success:
            reasons.append(f"Expected success={scenario.expected_success}, got success={result.success}")

        if scenario.expected_error and (not result.error or scenario.expected_error not in result.error):
            reasons.append(f"Expected error containing '{scenario.expected_error}', got '{result.error}'")

        if scenario.expected_output is not None and result.data != scenario.expected_output:
            reasons.append(f"Expected output {scenario.expected_output}, got {result.data}")

        return "; ".join(reasons)


# Pytest fixtures and utilities
def pytest_configure(config):
    """Configure pytest for agent testing."""
    config.addinivalue_line("markers", "agent_test: mark test as agent test")


@pytest.fixture
def agent_tester():
    """Pytest fixture for agent testing."""
    from ..agents.task import TaskAgent

    def _create_tester(agent_class=None, config=None):
        agent_class = agent_class or TaskAgent
        return AgentTester(agent_class, config)

    return _create_tester


@pytest.fixture
def llm_mocker():
    """Pytest fixture for LLM mocking."""
    return LLMMocker()

