from unittest.mock import Mock

from src.agent.planning.agent_step_executor import AgentStepExecutor
from src.agent.planning.gate import PlanningGate
from src.agent.planning.models import Plan, PlanStep, StepStatus
from src.agent.planning.plan_executor import PlanExecutor
from src.agent.planning.planner import Planner
from src.agent.validation.models import ValidationResult
from src.agent.validation.validator import Validator
from src.agent.workflow.final_answer import FinalAnswer
from src.agent.workflow.models import WorkflowResult
from src.agent.workflow.workflowrunner import WorkflowRunner


USER_INPUT = "我是油敏肌，有痘痘，想改善肤质，请帮我制定护肤方案。"
FINAL_ANSWER = (
    "根据你的油敏肌和痘痘情况，建议建立温和护肤方案，"
    "包括成分选择、风险控制和使用步骤。"
)


class CapturingWorkflowRunner:
    """Expose the WorkflowResult that PlanningGate intentionally unwraps."""

    def __init__(self, runner: WorkflowRunner) -> None:
        self.runner = runner
        self.calls: list[tuple[str, str]] = []
        self.result: WorkflowResult | None = None

    def run(self, user_input: str, session_id: str) -> WorkflowResult:
        self.calls.append((user_input, session_id))
        self.result = self.runner.run(user_input=user_input, session_id=session_id)
        return self.result


def test_complex_workflow_mvp_data_flow() -> None:
    plan = Plan(
        goal="为油敏肌且有痘痘的用户制定改善肤质的护肤方案",
        steps=[
            PlanStep(id=1, description="分析用户需求和肤质"),
            PlanStep(id=2, description="查询相关成分知识"),
            PlanStep(id=3, description="分析成分刺激风险和使用限制"),
            PlanStep(id=4, description="制定分阶段护肤方案"),
        ],
    )
    step_results = [
        "用户属于油敏肌，并存在痘痘问题",
        "查询得到相关护肤成分知识",
        "分析成分刺激风险和使用注意事项",
        "生成分阶段护肤方案",
    ]

    planner = Mock(spec=Planner)
    planner.create_plan.return_value = plan

    step_executor = Mock(spec=AgentStepExecutor)
    step_executor.execute.side_effect = step_results
    plan_executor = PlanExecutor(step_executor=step_executor)

    final_answer = Mock(spec=FinalAnswer)
    final_answer.synthesis.return_value = FINAL_ANSWER

    validation = ValidationResult(success=True, reasons=[])
    validator = Mock(spec=Validator)
    validator.validate.return_value = validation

    workflow_runner = WorkflowRunner(
        planner=planner,
        planexecutor=plan_executor,
        final_answer=final_answer,
        validator=validator,
    )
    capturing_runner = CapturingWorkflowRunner(workflow_runner)

    gate_llm = Mock()
    gate_llm.chat.return_value = "COMPLEX"
    direct_agent = Mock()
    gate = PlanningGate(
        llm=gate_llm,
        agent=direct_agent,
        workflow_runner=capturing_runner,
    )

    returned_answer = gate.choice(USER_INPUT, session_id="complex-mvp-session")

    # Planning Gate selected the complex route and did not use the direct Agent.
    gate_llm.chat.assert_called_once()
    gate_messages = gate_llm.chat.call_args.args[0]
    assert gate_messages[-1] == {"role": "user", "content": USER_INPUT}
    direct_agent.run.assert_not_called()
    assert capturing_runner.calls == [(USER_INPUT, "complex-mvp-session")]

    # Planner produced a non-empty plan that covers the user's main goals.
    planner.create_plan.assert_called_once_with(USER_INPUT)
    assert plan.steps
    assert len(plan.steps) >= 3
    plan_text = f"{plan.goal} {' '.join(step.description for step in plan.steps)}"
    for topic in ("油敏肌", "痘痘", "成分", "风险", "护肤方案"):
        assert topic in plan_text

    # The real PlanExecutor executed every mocked AgentStepExecutor step.
    assert step_executor.execute.call_count == len(plan.steps)
    executed_steps = [call.args[0] for call in step_executor.execute.call_args_list]
    assert executed_steps == plan.steps
    assert all(step.status is StepStatus.COMPLETED for step in plan.steps)
    assert all(step.result is not None for step in plan.steps)

    result = capturing_runner.result
    assert isinstance(result, WorkflowResult)
    assert len(result.step_results) == len(plan.steps)
    assert result.step_results == step_results

    # FinalAnswer and Validator received data collected by WorkflowRunner.
    final_answer.synthesis.assert_called_once_with(
        user_input=USER_INPUT,
        results=step_results,
    )
    validator.validate.assert_called_once_with(
        user_input=USER_INPUT,
        goal=plan.goal,
        final_answer=FINAL_ANSWER,
    )

    # WorkflowResult preserves the complete workflow output contract.
    assert result.user_input == USER_INPUT
    assert result.goal == plan.goal
    assert result.final_answer == final_answer.synthesis.return_value
    assert result.validation is validation
    assert result.validation.success is True
    assert result.validation.reasons == []
    assert returned_answer == result.final_answer
