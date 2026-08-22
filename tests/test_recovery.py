import pytest

from src.agent.planning.models import Plan
from src.agent.recovery.models import RecoveryExecutionContext
from src.agent.recovery.recoveryworkflow import RecoveryWorkflow


class FakeExecutor:
    def __init__(
        self,
        step_results: list[str] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.step_results = step_results if step_results is not None else []
        self.error = error
        self.received_plan: Plan | None = None

    def executor(self, plan: Plan) -> list[str]:
        self.received_plan = plan
        if self.error is not None:
            raise self.error
        return self.step_results


class FakeFinalAnswer:
    def __init__(self, answer: str = "recovered final answer") -> None:
        self.answer = answer
        self.received_user_input: str | None = None
        self.received_step_results: list[str] | None = None

    def generate(self, user_input: str, step_results: list[str]) -> str:
        self.received_user_input = user_input
        self.received_step_results = step_results
        return self.answer


def create_recovery_execution_context() -> RecoveryExecutionContext:
    return RecoveryExecutionContext(
        action="replan",
        plan=Plan(goal="recover cosmetic analysis"),
        use_input="Is this product suitable for sensitive skin?",
    )


def test_recovery_workflow_passes_context_plan_to_executor() -> None:
    context = create_recovery_execution_context()
    executor = FakeExecutor()
    workflow = RecoveryWorkflow(executor, FakeFinalAnswer())

    workflow.run(context)

    assert executor.received_plan is context.plan


def test_recovery_workflow_final_answer_receives_correct_data_sources() -> None:
    context = create_recovery_execution_context()
    executor = FakeExecutor(step_results=["ingredient result", "skin result"])
    final_answer = FakeFinalAnswer()
    workflow = RecoveryWorkflow(executor, final_answer)

    answer = workflow.run(context)

    assert final_answer.received_user_input == context.use_input
    assert final_answer.received_step_results is executor.step_results
    assert answer == final_answer.answer


def test_recovery_workflow_propagates_executor_error() -> None:
    context = create_recovery_execution_context()
    executor_error = RuntimeError("executor failed")
    workflow = RecoveryWorkflow(
        FakeExecutor(error=executor_error),
        FakeFinalAnswer(),
    )

    with pytest.raises(RuntimeError, match="executor failed") as exc_info:
        workflow.run(context)

    assert exc_info.value is executor_error
