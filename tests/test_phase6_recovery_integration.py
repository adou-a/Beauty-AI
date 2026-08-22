from dataclasses import dataclass

import pytest

from src.agent.planning.models import Plan, PlanStep, StepStatus
from src.agent.recovery.models import RecoveryContext, ReflectionResult, ReplanResult
from src.agent.recovery.recovery_manager import RecoveryManager
from src.agent.recovery.recoveryworkflow import RecoveryWorkflow
from src.agent.validation.models import ValidationResult
from src.agent.workflow.models import WorkflowResult
from src.agent.workflow.workflowrunner import WorkflowRunner


class FakePlanner:
    def __init__(self) -> None:
        self.plan = Plan(
            goal="evaluate cosmetic suitability",
            steps=[PlanStep(id=1, description="analyze ingredients")],
        )

    def create_plan(self, user_input: str) -> Plan:
        return self.plan


class FakePlanExecutor:
    def execute(self, plan, executor_context, workflow_state):
        plan.steps[0].status = StepStatus.COMPLETED
        plan.steps[0].result = "fake step result"
        return plan


class FakeInitialFinalAnswer:
    def synthesis(self, user_input: str, results: list[str]) -> str:
        return "initial answer"


class SequenceValidator:
    def __init__(self, results: list[ValidationResult]) -> None:
        self.results = results
        self.calls: list[tuple[str, str, str]] = []

    def validate(
        self,
        user_input: str,
        goal: str,
        final_answer: str,
    ) -> ValidationResult:
        if len(self.calls) >= len(self.results):
            raise AssertionError("validator was called more than expected")
        self.calls.append((user_input, goal, final_answer))
        return self.results[len(self.calls) - 1]


class FakeReflection:
    def __init__(self) -> None:
        self.call_count = 0
        self.received_context: RecoveryContext | None = None

    def analyze(self, context: RecoveryContext) -> ReflectionResult:
        self.call_count += 1
        self.received_context = context
        return ReflectionResult(
            need_replan=False,
            failure_type="validation_failure",
            missing_information=[],
            reason="retry the recovery workflow",
        )


class ReplannerThatMustNotRun:
    def replan(
        self,
        recovery_context: RecoveryContext,
        reflection_result: ReflectionResult,
    ) -> ReplanResult:
        raise AssertionError("replanner must not run for this integration path")


class FakeRecoveryExecutor:
    def __init__(self) -> None:
        self.call_count = 0
        self.received_plan: Plan | None = None

    def executor(self, plan: Plan) -> list[str]:
        self.call_count += 1
        self.received_plan = plan
        return ["fake recovery step result"]


class FakeRecoveryFinalAnswer:
    def __init__(self) -> None:
        self.answer = "recovered answer"
        self.call_count = 0

    def generate(self, user_input: str, step_results: list[str]) -> str:
        self.call_count += 1
        return self.answer


class RecordingRecoveryManager:
    def __init__(self, delegate: RecoveryManager) -> None:
        self.delegate = delegate
        self.call_count = 0
        self.received_context: RecoveryContext | None = None

    def recover(self, context: RecoveryContext):
        self.call_count += 1
        self.received_context = context
        return self.delegate.recover(context)


class FailingRecoveryManager:
    def __init__(self, error: Exception) -> None:
        self.error = error
        self.call_count = 0

    def recover(self, context: RecoveryContext):
        self.call_count += 1
        raise self.error


@dataclass
class RecoveryIntegrationHarness:
    runner: WorkflowRunner
    validator: SequenceValidator
    recovery_manager: RecordingRecoveryManager
    reflection: FakeReflection
    recovery_executor: FakeRecoveryExecutor
    recovery_final_answer: FakeRecoveryFinalAnswer


def create_harness(
    validation_results: list[ValidationResult],
) -> RecoveryIntegrationHarness:
    validator = SequenceValidator(validation_results)
    reflection = FakeReflection()
    recovery_executor = FakeRecoveryExecutor()
    recovery_final_answer = FakeRecoveryFinalAnswer()
    recovery_workflow = RecoveryWorkflow(
        executor=recovery_executor,
        final_answer=recovery_final_answer,
    )
    recovery_manager = RecordingRecoveryManager(
        RecoveryManager(
            reflection=reflection,
            replanner=ReplannerThatMustNotRun(),
            workflow=recovery_workflow,
        )
    )
    runner = WorkflowRunner(
        planner=FakePlanner(),
        planexecutor=FakePlanExecutor(),
        final_answer=FakeInitialFinalAnswer(),
        validator=validator,
        recovery_manager=recovery_manager,
    )
    return RecoveryIntegrationHarness(
        runner=runner,
        validator=validator,
        recovery_manager=recovery_manager,
        reflection=reflection,
        recovery_executor=recovery_executor,
        recovery_final_answer=recovery_final_answer,
    )


def test_recovery_success_revalidates_and_returns_successful_workflow_result() -> None:
    first_validation = ValidationResult(success=False, reasons=["retry required"])
    second_validation = ValidationResult(success=True, reasons=[])
    harness = create_harness([first_validation, second_validation])

    result = harness.runner.run("fake user input", "session-success")

    assert harness.recovery_manager.call_count == 1
    assert harness.reflection.call_count == 1
    assert harness.recovery_executor.call_count == 1
    assert harness.recovery_final_answer.call_count == 1
    assert len(harness.validator.calls) == 2
    assert harness.validator.calls[1][2] == harness.recovery_final_answer.answer
    assert isinstance(result, WorkflowResult)
    assert result.validation is second_validation
    assert result.validation.success is True


def test_recovery_failure_stops_after_second_validation() -> None:
    first_validation = ValidationResult(success=False, reasons=["retry required"])
    second_validation = ValidationResult(success=False, reasons=["still invalid"])
    harness = create_harness([first_validation, second_validation])

    result = harness.runner.run("fake user input", "session-failure")

    assert harness.recovery_manager.call_count == 1
    assert harness.recovery_executor.call_count == 1
    assert len(harness.validator.calls) == 2
    assert isinstance(result, WorkflowResult)
    assert result.validation is second_validation
    assert result.validation.success is False


def test_recovery_manager_error_propagates_without_goal_failure_conversion() -> None:
    first_validation = ValidationResult(success=False, reasons=["retry required"])
    recovery_error = RuntimeError("recovery workflow failed")
    validator = SequenceValidator([first_validation])
    recovery_manager = FailingRecoveryManager(recovery_error)
    runner = WorkflowRunner(
        planner=FakePlanner(),
        planexecutor=FakePlanExecutor(),
        final_answer=FakeInitialFinalAnswer(),
        validator=validator,
        recovery_manager=recovery_manager,
    )

    with pytest.raises(RuntimeError, match="recovery workflow failed") as exc_info:
        runner.run("fake user input", "session-error")

    assert exc_info.value is recovery_error
    assert recovery_manager.call_count == 1
    assert len(validator.calls) == 1
