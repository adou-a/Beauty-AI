import pytest

from src.agent.planning.models import Plan, PlanStep, StepStatus
from src.agent.recovery.models import (
    RecoveryContext,
    RecoveryResult,
    ReflectionResult,
)
from src.agent.recovery.recovery_manager import RecoveryManager
from src.agent.validation.models import ValidationResult


class FailingReflection:
    def analyze(self, context):
        raise RuntimeError("reflection failed")


class RecordingReflection:
    def __init__(self, result: ReflectionResult):
        self.result = result
        self.received_context = None

    def analyze(self, context):
        self.received_context = context
        return self.result


class FakeRecoveryFinalAnswer:
    def __init__(self, answer: str):
        self.answer = answer
        self.received_context = None

    def generate(self, context):
        self.received_context = context
        return self.answer


def test_recovery_context_has_expected_format_and_sources():
    step_result = "ingredient-analysis-result"
    plan = Plan(
        goal="analyze cosmetic ingredients",
        steps=[
            PlanStep(
                id=1,
                description="analyze ingredients",
                status=StepStatus.COMPLETED,
                result=step_result,
            )
        ],
    )
    validation_result = ValidationResult(
        success=False,
        reasons=["missing skin suitability analysis"],
    )
    context = RecoveryContext(
        user_input="Is this product suitable for sensitive skin?",
        goal=plan.goal,
        old_plan=plan,
        step_results=[step_result],
        final_answer="The ingredient analysis is incomplete.",
        validation_result=validation_result,
    )
    reflection = RecordingReflection(
        ReflectionResult(
            need_replan=False,
            failure_type="answer_incomplete",
            missing_information=["skin suitability analysis"],
            reason="The answer is incomplete.",
        )
    )
    manager = RecoveryManager(
        reflection,
        final_answer=FakeRecoveryFinalAnswer("recovered answer"),
    )

    manager.recover(context)

    assert isinstance(context.user_input, str)
    assert context.goal == plan.goal
    assert context.old_plan is plan
    assert context.step_results == [plan.steps[0].result]
    assert isinstance(context.final_answer, str)
    assert context.validation_result is validation_result
    assert reflection.received_context is context


def test_recovery_manager_returns_recovery_result_not_reflection_result():
    context = RecoveryContext(
        user_input="Can I use retinol every day?",
        goal="evaluate retinol suitability",
        old_plan=Plan(goal="evaluate retinol suitability"),
        step_results=["retinol information collected"],
        final_answer="Daily use is recommended.",
        validation_result=ValidationResult(
            success=False,
            reasons=["missing tolerance assessment"],
        ),
    )
    reflection_result = ReflectionResult(
        need_replan=False,
        failure_type="answer_incomplete",
        missing_information=["skin tolerance"],
        reason="The answer lacks a skin tolerance assessment.",
    )
    reflection = RecordingReflection(reflection_result)
    final_answer = FakeRecoveryFinalAnswer("Use retinol gradually.")

    result = RecoveryManager(
        reflection,
        final_answer=final_answer,
    ).recover(context)

    assert reflection.received_context is context
    assert not isinstance(result, ReflectionResult)
    assert isinstance(result, RecoveryResult)
    assert result.recovered is True
    assert result.final_answer == "Use retinol gradually."


def test_recovery_manager_propagates_reflection_system_error():
    context = RecoveryContext(
        user_input="Can I use retinol every day?",
        goal="evaluate retinol suitability",
        old_plan=Plan(goal="evaluate retinol suitability"),
        step_results=["retinol information collected"],
        final_answer="Daily use is recommended.",
        validation_result=ValidationResult(
            success=False,
            reasons=["missing tolerance assessment"],
        ),
    )
    manager = RecoveryManager(FailingReflection())

    with pytest.raises(RuntimeError, match="reflection failed"):
        manager.recover(context)
