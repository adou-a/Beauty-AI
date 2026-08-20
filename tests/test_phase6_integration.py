import pytest

from src.agent.planning.agent_step_executor import AgentStepExecutor
from src.agent.planning.gate import PlanningGate
from src.agent.planning.models import Plan, PlanStep, StepStatus
from src.agent.planning.plan_executor import PlanExecutionError, PlanExecutor
from src.agent.validation.models import ValidationResult
from src.agent.workflow.models import WorkflowResult
from src.agent.workflow.workflowrunner import WorkflowRunner
from src.agent.workflow.workflowstatus import WorkflowStatus


class FixedGateLLM:
    def __init__(self, decision):
        self.decision = decision

    def chat(self, messages):
        return self.decision


class RecordingAgent:
    def __init__(self):
        self.calls = []

    def run(self, session_id, user_input):
        self.calls.append((session_id, user_input))
        return f"agent-result-{len(self.calls)}"


class RecordingWorkflowRunner:
    def __init__(self):
        self.calls = []

    def run(self, user_input, session_id):
        self.calls.append((user_input, session_id))
        return WorkflowResult(
            user_input=user_input,
            goal="workflow-goal",
            step_results=[],
            final_answer="workflow-result",
            validation=ValidationResult(success=True, reasons=[]),
        )


class FakeFinalAnswer:
    def synthesis(self, user_input, results):
        return "final-answer"


class FakeValidator:
    def validate(self, user_input, goal, final_answer):
        return ValidationResult(success=True, reasons=[])


class FakePlanner:
    def __init__(self):
        self.plan = Plan(
            goal="分析视黄醇刺激并制定方案",
            steps=[
                PlanStep(id=1, description="分析刺痛原因"),
                PlanStep(id=2, description="分析脱皮风险"),
                PlanStep(id=3, description="制定四周方案"),
            ],
        )

    def create_plan(self, user_input):
        return self.plan


class StateCapturingPlanExecutor:
    def __init__(self, step_executor):
        self.delegate = PlanExecutor(step_executor)
        self.workflow_state = None

    def execute(self, plan, executor_context, workflow_state):
        self.workflow_state = workflow_state
        return self.delegate.execute(plan, executor_context, workflow_state)


def test_simple_query_routes_to_agent_only():
    user_input = "烟酰胺有什么作用？"
    agent = RecordingAgent()
    workflow_runner = RecordingWorkflowRunner()
    gate = PlanningGate(
        llm=FixedGateLLM("SIMPLE"),
        agent=agent,
        workflow_runner=workflow_runner,
    )

    result = gate.choice(user_input, "session-simple")

    assert result == "agent-result-1"
    assert agent.calls == [("session-simple", user_input)]
    assert workflow_runner.calls == []


def test_complex_query_routes_to_workflow_only():
    user_input = """我是敏感肌，
使用视黄醇后刺痛脱皮，
请分析原因并制定四周方案。"""
    agent = RecordingAgent()
    workflow_runner = RecordingWorkflowRunner()
    gate = PlanningGate(
        llm=FixedGateLLM("COMPLEX"),
        agent=agent,
        workflow_runner=workflow_runner,
    )

    result = gate.choice(user_input, "session-complex")

    assert result == "workflow-result"
    assert workflow_runner.calls == [(user_input, "session-complex")]
    assert agent.calls == []


def test_workflow_executes_and_saves_all_three_steps():
    planner = FakePlanner()
    agent = RecordingAgent()
    plan_executor = StateCapturingPlanExecutor(AgentStepExecutor(agent))
    runner = WorkflowRunner(
        planner=planner,
        planexecutor=plan_executor,
        final_answer=FakeFinalAnswer(),
        validator=FakeValidator(),
    )

    runner.run("复杂护肤请求", "session-workflow")

    assert len(agent.calls) == 3
    assert [step.status for step in planner.plan.steps] == [
        StepStatus.COMPLETED,
        StepStatus.COMPLETED,
        StepStatus.COMPLETED,
    ]
    assert [step.result for step in planner.plan.steps] == [
        "agent-result-1",
        "agent-result-2",
        "agent-result-3",
    ]
    assert plan_executor.workflow_state.status == WorkflowStatus.COMPLETED


def test_step_two_failure_stops_workflow_and_preserves_states():
    class FailingOnSecondStepAgent(RecordingAgent):
        def run(self, session_id, user_input):
            self.calls.append((session_id, user_input))
            if len(self.calls) == 2:
                raise RuntimeError("step 2 failed")
            return f"agent-result-{len(self.calls)}"

    planner = FakePlanner()
    agent = FailingOnSecondStepAgent()
    plan_executor = StateCapturingPlanExecutor(AgentStepExecutor(agent))
    runner = WorkflowRunner(
        planner=planner,
        planexecutor=plan_executor,
        final_answer=FakeFinalAnswer(),
        validator=FakeValidator(),
    )

    with pytest.raises(PlanExecutionError):
        runner.run("复杂护肤请求", "session-failure")

    assert [step.status for step in planner.plan.steps] == [
        StepStatus.COMPLETED,
        StepStatus.FAILED,
        StepStatus.PENDING,
    ]
    assert plan_executor.workflow_state.status == WorkflowStatus.FAILED
