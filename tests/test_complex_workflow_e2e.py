from unittest.mock import patch

from src.agent.planning.agent_step_executor import AgentStepExecutor
from src.agent.planning.gate import PlanningGate
from src.agent.planning.models import Plan, PlanStep, StepStatus
from src.agent.planning.plan_executor import PlanExecutor
from src.agent.validation.models import ValidationResult
from src.agent.workflow.models import WorkflowResult
from src.agent.workflow.workflowrunner import WorkflowRunner


USER_INPUT = (
    "我是敏感肌，最近第一次使用视黄醇产品后出现刺痛和脱皮。"
    "请分析可能原因，并结合风险制定一个循序渐进的使用方案，"
    "同时告诉我需要注意哪些事项。"
)
SESSION_ID = "complex-workflow-e2e"
GOAL = "分析敏感肌使用视黄醇后的风险和使用方案"


class FixedGateLLM:
    def __init__(self) -> None:
        self.messages: list[list[dict[str, str]]] = []

    def chat(self, messages: list[dict[str, str]]) -> str:
        self.messages.append(messages)
        return "COMPLEX"


class FakePlanner:
    def __init__(self) -> None:
        self.received_user_input: str | None = None
        self.plan = Plan(
            goal=GOAL,
            steps=[
                PlanStep(id=1, description="分析刺痛脱皮原因"),
                PlanStep(id=2, description="分析敏感肌使用风险"),
                PlanStep(id=3, description="制定使用方案"),
            ],
        )

    def create_plan(self, user_input: str) -> Plan:
        self.received_user_input = user_input
        return self.plan


class FakeAgent:
    RESULTS = (
        "step1-result",
        "step2-result",
        "step3-result",
    )

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run(self, session_id: str, prompt: str) -> str:
        self.calls.append((session_id, prompt))
        return self.RESULTS[len(self.calls) - 1]


class FakeFinalAnswer:
    def __init__(self) -> None:
        self.received_user_input: str | None = None
        self.received_results: list[str] | None = None

    def synthesis(self, user_input: str, results: list[str]) -> str:
        self.received_user_input = user_input
        self.received_results = list(results)
        return "final-answer"


class FakeValidator:
    def __init__(self) -> None:
        self.received_user_input: str | None = None
        self.received_goal: str | None = None
        self.received_final_answer: str | None = None
        self.validation_result = ValidationResult(success=True, reasons=[])

    def validate(
        self,
        user_input: str,
        goal: str,
        final_answer: str,
    ) -> ValidationResult:
        self.received_user_input = user_input
        self.received_goal = goal
        self.received_final_answer = final_answer
        return self.validation_result


def test_complex_workflow_runs_end_to_end() -> None:
    gate_llm = FixedGateLLM()
    planner = FakePlanner()
    workflow_agent = FakeAgent()
    final_answer = FakeFinalAnswer()
    validator = FakeValidator()
    plan_executor = PlanExecutor(
        step_executor=AgentStepExecutor(agent=workflow_agent)
    )
    workflow_runner = WorkflowRunner(
        planner=planner,
        planexecutor=plan_executor,
        final_answer=final_answer,
        validator=validator,
    )
    gate = PlanningGate(
        llm=gate_llm,
        agent=workflow_agent,
        workflow_runner=workflow_runner,
    )

    captured_results: list[WorkflowResult] = []
    real_workflow_run = workflow_runner.run

    def capture_real_workflow_run(
        *,
        user_input: str,
        session_id: str,
    ) -> WorkflowResult:
        result = real_workflow_run(
            user_input=user_input,
            session_id=session_id,
        )
        captured_results.append(result)
        return result

    with patch.object(
        gate,
        "_get_decision",
        wraps=gate._get_decision,
    ) as decision_spy, patch.object(
        workflow_runner,
        "run",
        side_effect=capture_real_workflow_run,
    ) as workflow_run_spy:
        gate_result = gate.choice(user_input=USER_INPUT, session_id=SESSION_ID)

    assert type(gate) is PlanningGate
    assert type(workflow_runner) is WorkflowRunner
    assert type(plan_executor) is PlanExecutor
    decision_spy.assert_called_once_with("COMPLEX")
    assert gate_llm.messages[0][-1] == {
        "role": "user",
        "content": USER_INPUT,
    }
    workflow_run_spy.assert_called_once_with(
        user_input=USER_INPUT,
        session_id=SESSION_ID,
    )

    assert planner.received_user_input == USER_INPUT
    assert len(workflow_agent.calls) == 3
    assert [session_id for session_id, _ in workflow_agent.calls] == [
        SESSION_ID,
        SESSION_ID,
        SESSION_ID,
    ]
    assert [
        description in prompt
        for description, (_, prompt) in zip(
            [step.description for step in planner.plan.steps],
            workflow_agent.calls,
            strict=True,
        )
    ] == [True, True, True]

    assert [step.status for step in planner.plan.steps] == [
        StepStatus.COMPLETED,
        StepStatus.COMPLETED,
        StepStatus.COMPLETED,
    ]
    assert [step.result for step in planner.plan.steps] == [
        "step1-result",
        "step2-result",
        "step3-result",
    ]

    expected_step_results = [
        "step1-result",
        "step2-result",
        "step3-result",
    ]
    assert final_answer.received_user_input == USER_INPUT
    assert final_answer.received_results == expected_step_results
    assert validator.received_user_input == USER_INPUT
    assert validator.received_goal == GOAL
    assert validator.received_final_answer == "final-answer"

    assert len(captured_results) == 1
    result = captured_results[0]
    assert type(result) is WorkflowResult
    assert result.user_input == USER_INPUT
    assert result.goal == GOAL
    assert result.step_results == expected_step_results
    assert result.final_answer == "final-answer"
    assert result.validation == ValidationResult(success=True, reasons=[])
    assert gate_result == result.final_answer
