import pytest

from src.agent.planning.models import PlanStep,Plan,StepStatus
from src.agent.planning.plan_executor import PlanExecutor,PlanExecutionError
from src.agent.planning.agent_step_executor import AgentStepExecutionError,AgentStepExecutor
from src.exceptions.agent_exception import ToolExecutionError


class FakeAgent:
    def __init__(self):
        self.calls = []


    def run(self,session_id: str, user_input: str) -> str:

        self.calls.append({
            'session_id': session_id,
            'user_input': user_input
        })


        return(f'agent-result-{len(self.calls)}')

def test_agent_step_executor_returns_agent_result():

    agent = FakeAgent()

    executor = AgentStepExecutor(
        agent=agent,
        session_id="workflow-001",
        goal="制定视黄醇耐受方案",
    )

    step = PlanStep(
        id=1,
        description="获取视黄醇基础信息",
    )

    result = executor.execute(
        step
    )

    assert (
        result
        == "agent-result-1"
    )

    assert len(
        agent.calls
    ) == 1


def test_agent_step_prompt_contains_goal_and_step():

    agent = FakeAgent()

    executor = AgentStepExecutor(
        agent=agent,
        session_id="workflow-001",
        goal="制定四周视黄醇耐受方案",
    )

    step = PlanStep(
        id=1,
        description="分析敏感肌刺激风险",
    )

    executor.execute(
        step
    )

    prompt = (
        agent.calls[0]["user_input"]
    )

    assert (
        "制定四周视黄醇耐受方案"
        in prompt
    )

    assert (
        "分析敏感肌刺激风险"
        in prompt
    )

def test_steps_use_same_workflow_session():

    agent = FakeAgent()

    step_executor = AgentStepExecutor(
        agent=agent,
        session_id="workflow-001",
        goal="test goal",
    )

    step_executor.execute(
        PlanStep(
            id=1,
            description="step 1",
        )
    )

    step_executor.execute(
        PlanStep(
            id=2,
            description="step 2",
        )
    )

    assert (
        agent.calls[0]["session_id"]
        == "workflow-001"
    )

    assert (
        agent.calls[1]["session_id"]
        == "workflow-001"
    )

class EmptyFakeAgent:

    def run(
        self,
        session_id: str,
        user_input: str,
    ) -> str:

        return ""


def test_empty_agent_result_is_rejected():

    executor = AgentStepExecutor(
        agent=EmptyFakeAgent(),
        session_id="workflow-001",
        goal="test goal",
    )

    step = PlanStep(
        id=1,
        description="test step",
    )

    with pytest.raises(
        AgentStepExecutionError
    ):
        executor.execute(
            step
        )

class FailingFakeAgent:

    def run(
        self,
        session_id: str,
        user_input: str,
    ) -> str:

        raise RuntimeError(
            "fake agent failure"
        )


class ToolExecutionFailingAgent:

    def run(
        self,
        session_id: str,
        user_input: str,
    ) -> str:

        raise ToolExecutionError(
            "tool execution failed"
        )


def test_tool_execution_error_is_wrapped():

    executor = AgentStepExecutor(
        agent=ToolExecutionFailingAgent(),
    )

    step = PlanStep(
        id=1,
        description="test step",
    )

    class ExecutorContext:
        session_id = "workflow-001"

    with pytest.raises(
        AgentStepExecutionError
    ) as exc_info:
        executor.execute(
            step,
            ExecutorContext(),
            "test goal",
        )

    assert isinstance(
        exc_info.value.__cause__,
        ToolExecutionError,
    )

def test_agent_failure_is_wrapped():

    executor = AgentStepExecutor(
        agent=FailingFakeAgent(),
        session_id="workflow-001",
        goal="test goal",
    )

    step = PlanStep(
        id=1,
        description="test step",
    )

    with pytest.raises(
        AgentStepExecutionError
    ):
        executor.execute(
            step
        )


def test_plan_executor_uses_agent_for_each_step():

    plan = Plan(
        goal="制定视黄醇耐受方案",
        steps=[
            PlanStep(
                id=1,
                description="获取视黄醇信息",
            ),
            PlanStep(
                id=2,
                description="分析敏感肌风险",
            ),
            PlanStep(
                id=3,
                description="制定使用建议",
            ),
        ],
    )

    agent = FakeAgent()

    step_executor = AgentStepExecutor(
        agent=agent,
        session_id="workflow-001",
        goal=plan.goal,
    )

    plan_executor = PlanExecutor(
        step_executor=step_executor,
    )

    result_plan = (
        plan_executor.execute(
            plan
        )
    )

    assert len(
        agent.calls
    ) == 3

    assert (
        result_plan.steps[0].result
        == "agent-result-1"
    )

    assert (
        result_plan.steps[1].result
        == "agent-result-2"
    )

    assert (
        result_plan.steps[2].result
        == "agent-result-3"
    )

    for step in result_plan.steps:

        assert (
            step.status
            == StepStatus.COMPLETED
        )
