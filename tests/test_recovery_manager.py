import pytest

from src.agent.planning.models import Plan
from src.agent.recovery.models import (
    RecoveryContext,
    RecoveryExecutionContext,
    RecoveryResult,
    ReflectionResult,
    ReplanResult,
)
from src.agent.recovery.recovery_manager import RecoveryManager
from src.agent.validation.models import ValidationResult


class FakeReflection:
    def __init__(
        self,
        result: ReflectionResult,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.received_context: RecoveryContext | None = None
        self.call_count = 0

    def analyze(self, context: RecoveryContext) -> ReflectionResult:
        self.call_count += 1
        self.received_context = context
        if self.error is not None:
            raise self.error
        return self.result


class FakeReplanner:
    def __init__(
        self,
        result: ReplanResult,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.received_context: RecoveryContext | None = None
        self.received_reflection_result: ReflectionResult | None = None
        self.call_count = 0

    def replan(
        self,
        recovery_context: RecoveryContext,
        reflection_result: ReflectionResult,
    ) -> ReplanResult:
        self.call_count += 1
        self.received_context = recovery_context
        self.received_reflection_result = reflection_result
        if self.error is not None:
            raise self.error
        return self.result


class FakeWorkflow:
    def __init__(
        self,
        answer: str = "fake recovered answer",
        error: Exception | None = None,
    ) -> None:
        self.answer = answer
        self.error = error
        self.received_execution_context: RecoveryExecutionContext | None = None
        self.call_count = 0

    def run(self, execution_context: RecoveryExecutionContext) -> str:
        self.call_count += 1
        self.received_execution_context = execution_context
        if self.error is not None:
            raise self.error
        return self.answer


def create_recovery_context() -> RecoveryContext:
    old_plan = Plan(goal="analyze sensitive-skin suitability")
    return RecoveryContext(
        user_input="Is this cosmetic suitable for sensitive skin?",
        goal=old_plan.goal,
        old_plan=old_plan,
        step_results=["ingredient analysis incomplete"],
        final_answer="The previous answer was incomplete.",
        validation_result=ValidationResult(
            success=False,
            reasons=["missing skin suitability analysis"],
        ),
    )


def create_reflection_result(need_replan: bool) -> ReflectionResult:
    return ReflectionResult(
        need_replan=need_replan,
        failure_type="incomplete_answer",
        missing_information=["skin suitability"],
        reason="The previous answer missed required information.",
    )


def create_replan_result() -> ReplanResult:
    return ReplanResult(
        new_plan=Plan(goal="replan sensitive-skin suitability analysis"),
        reason="Additional analysis is required.",
    )


def test_recovery_manager_passes_recovery_context_to_reflection() -> None:
    context = create_recovery_context()
    reflection_result = create_reflection_result(need_replan=False)
    reflection = FakeReflection(reflection_result)
    manager = RecoveryManager(
        reflection=reflection,
        replanner=FakeReplanner(create_replan_result()),
        workflow=FakeWorkflow(),
    )

    manager.recover(context)

    assert reflection.call_count == 1
    assert reflection.received_context is context


def test_recovery_manager_calls_replanner_when_replan_is_needed() -> None:
    context = create_recovery_context()
    replanner = FakeReplanner(create_replan_result())
    manager = RecoveryManager(
        reflection=FakeReflection(create_reflection_result(need_replan=True)),
        replanner=replanner,
        workflow=FakeWorkflow(),
    )

    manager.recover(context)

    assert replanner.call_count == 1


def test_recovery_manager_does_not_call_replanner_when_replan_is_not_needed() -> None:
    context = create_recovery_context()
    replanner = FakeReplanner(create_replan_result())
    manager = RecoveryManager(
        reflection=FakeReflection(create_reflection_result(need_replan=False)),
        replanner=replanner,
        workflow=FakeWorkflow(),
    )

    manager.recover(context)

    assert replanner.call_count == 0


def test_recovery_manager_passes_context_and_reflection_result_to_replanner() -> None:
    context = create_recovery_context()
    reflection_result = create_reflection_result(need_replan=True)
    replanner = FakeReplanner(create_replan_result())
    manager = RecoveryManager(
        reflection=FakeReflection(reflection_result),
        replanner=replanner,
        workflow=FakeWorkflow(),
    )

    manager.recover(context)

    assert replanner.received_context is context
    assert replanner.received_reflection_result is reflection_result


def test_recovery_manager_passes_replan_action_plan_and_user_input_to_workflow() -> None:
    context = create_recovery_context()
    replan_result = create_replan_result()
    workflow = FakeWorkflow(answer="fake workflow answer")
    manager = RecoveryManager(
        reflection=FakeReflection(create_reflection_result(need_replan=True)),
        replanner=FakeReplanner(replan_result),
        workflow=workflow,
    )

    manager.recover(context)

    execution_context = workflow.received_execution_context
    assert workflow.call_count == 1
    assert execution_context == RecoveryExecutionContext(
        action="replan",
        plan=replan_result.new_plan,
        use_input=context.user_input,
    )


def test_recovery_manager_returns_recovery_result_with_workflow_answer() -> None:
    context = create_recovery_context()
    workflow = FakeWorkflow(answer="fake workflow answer")
    manager = RecoveryManager(
        reflection=FakeReflection(create_reflection_result(need_replan=False)),
        replanner=FakeReplanner(create_replan_result()),
        workflow=workflow,
    )

    result = manager.recover(context)

    assert result == RecoveryResult(
        recovered=True,
        final_answer=workflow.answer,
    )


def test_recovery_manager_propagates_reflection_error() -> None:
    context = create_recovery_context()
    reflection_error = RuntimeError("reflection failed")
    manager = RecoveryManager(
        reflection=FakeReflection(
            create_reflection_result(need_replan=True),
            error=reflection_error,
        ),
        replanner=FakeReplanner(create_replan_result()),
        workflow=FakeWorkflow(),
    )

    with pytest.raises(RuntimeError, match="reflection failed") as exc_info:
        manager.recover(context)

    assert exc_info.value is reflection_error


def test_recovery_manager_propagates_replanner_error() -> None:
    context = create_recovery_context()
    replanner_error = RuntimeError("replanner failed")
    manager = RecoveryManager(
        reflection=FakeReflection(create_reflection_result(need_replan=True)),
        replanner=FakeReplanner(
            create_replan_result(),
            error=replanner_error,
        ),
        workflow=FakeWorkflow(),
    )

    with pytest.raises(RuntimeError, match="replanner failed") as exc_info:
        manager.recover(context)

    assert exc_info.value is replanner_error


def test_recovery_manager_propagates_workflow_error() -> None:
    context = create_recovery_context()
    workflow_error = RuntimeError("workflow failed")
    manager = RecoveryManager(
        reflection=FakeReflection(create_reflection_result(need_replan=False)),
        replanner=FakeReplanner(create_replan_result()),
        workflow=FakeWorkflow(error=workflow_error),
    )

    with pytest.raises(RuntimeError, match="workflow failed") as exc_info:
        manager.recover(context)

    assert exc_info.value is workflow_error
