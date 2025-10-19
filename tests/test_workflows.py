"""Tests for workflow functionality."""

import pytest
from src.workflows.models import WorkflowConfig, WorkflowStep, Workflow
from src.workflows.engine import WorkflowEngine


@pytest.fixture
def workflow_config():
    """Create a test workflow configuration."""
    return WorkflowConfig(
        name="test_workflow",
        description="Test workflow",
        timeout=300,
        parallel_execution=False,
        on_failure="stop"
    )


@pytest.fixture
def workflow_steps():
    """Create test workflow steps."""
    return [
        WorkflowStep(
            id="step1",
            name="First Step",
            agent_type="task",
            agent_config={
                "name": "step1_agent",
                "description": "First step agent",
                "task_type": "test",
                "max_retries": 3,
                "timeout": 60
            },
            inputs={"input": "test"},
            depends_on=[],
            timeout=60
        ),
        WorkflowStep(
            id="step2",
            name="Second Step",
            agent_type="task",
            agent_config={
                "name": "step2_agent",
                "description": "Second step agent",
                "task_type": "test",
                "max_retries": 3,
                "timeout": 60
            },
            inputs={"input": "{{step1.output}}"},
            depends_on=["step1"],
            timeout=60
        )
    ]


@pytest.mark.asyncio
async def test_workflow_creation(workflow_config, workflow_steps):
    """Test workflow creation."""
    workflow = Workflow(
        id="test_workflow_1",
        config=workflow_config,
        steps=workflow_steps
    )

    assert workflow.id == "test_workflow_1"
    assert workflow.config.name == "test_workflow"
    assert len(workflow.steps) == 2


@pytest.mark.asyncio
async def test_workflow_engine_dependency_graph():
    """Test workflow engine dependency graph building."""
    engine = WorkflowEngine()

    steps = [
        WorkflowStep(
            id="step1",
            name="Step 1",
            agent_type="task",
            agent_config={},
            inputs={},
            depends_on=[],
            timeout=60
        ),
        WorkflowStep(
            id="step2",
            name="Step 2",
            agent_type="task",
            agent_config={},
            inputs={},
            depends_on=["step1"],
            timeout=60
        ),
        WorkflowStep(
            id="step3",
            name="Step 3",
            agent_type="task",
            agent_config={},
            inputs={},
            depends_on=["step1"],
            timeout=60
        )
    ]

    graph = engine._build_dependency_graph(steps)

    # First level should have step1
    assert len(graph) == 2
    assert graph[0][0].id == "step1"

    # Second level should have step2 and step3
    assert len(graph[1]) == 2
    assert set(s.id for s in graph[1]) == {"step2", "step3"}


@pytest.mark.asyncio
async def test_workflow_step_creation():
    """Test workflow step model."""
    step = WorkflowStep(
        id="test_step",
        name="Test Step",
        agent_type="task",
        agent_config={
            "name": "test_agent",
            "description": "Test agent",
            "task_type": "test",
            "max_retries": 3,
            "timeout": 60
        },
        inputs={"key": "value"},
        depends_on=[],
        timeout=60,
        condition="true"
    )

    assert step.id == "test_step"
    assert step.name == "Test Step"
    assert step.agent_type == "task"
    assert step.timeout == 60
    assert step.condition == "true"

