from unittest.mock import patch

import pytest

from src.agent.planning.models import Plan, PlanStep
from src.agent.workflow.models import ValidationResult, WorkflowResult
from src.agent.workflow.validator import Validator
from src.agent.workflow.workflowrunner import WorkflowRunner


class FakePlanner:
    def __init__(self):
        self.plan = Plan(
            goal="planner-goal",
            steps=[PlanStep(id=1, description="step-1")],
        )

    def create_plan(self, user_input):
        return self.plan


class FakePlanExecutor:
    def execute(self, plan, executor_context, workflow_state):
        plan.steps[0].result = "step-result"
        return plan


class FakeFinalAnswer:
    def __init__(self):
        self.answer = "final-answer-output"

    def synthesis(self, user_input, results):
        return self.answer


class FakeValidator:
    def __init__(self, validation_result):
        self.validation_result = validation_result
        self.calls = []

    def validate(self, user_input, goal, final_answer):
        self.calls.append(
            {
                "user_input": user_input,
                "goal": goal,
                "final_answer": final_answer,
            }
        )
        return self.validation_result


def create_runner(validator):
    return WorkflowRunner(
        planner=FakePlanner(),
        planexecutor=FakePlanExecutor(),
        final_answer=FakeFinalAnswer(),
        validator=validator,
    )


def test_success_validation_contract():
    validation = ValidationResult(success=True, reasons=[])
    validator = FakeValidator(validation)
    runner = create_runner(validator)

    result = runner.run("original-user-input", "session-validation")

    assert validator.calls == [
        {
            "user_input": "original-user-input",
            "goal": "planner-goal",
            "final_answer": "final-answer-output",
        }
    ]
    assert isinstance(result, WorkflowResult)
    assert result.validation is validation
    assert result.validation.success is True
    assert result.validation.reasons == []


def test_goal_validation_failure_is_normal_workflow_result():
    validation = ValidationResult(
        success=False,
        reasons=["missing risk analysis"],
    )
    runner = create_runner(FakeValidator(validation))

    result = runner.run("original-user-input", "session-validation")

    assert isinstance(result, WorkflowResult)
    assert result.validation.success is False
    assert result.validation.reasons == ["missing risk analysis"]


def test_validator_system_failure_propagates_without_fake_result():
    class FailingValidator:
        def validate(self, user_input, goal, final_answer):
            raise RuntimeError("validator failed")

    runner = create_runner(FailingValidator())

    with patch(
        "src.agent.workflow.workflowrunner.WorkflowResult"
    ) as workflow_result_constructor:
        with pytest.raises(RuntimeError, match="validator failed"):
            runner.run("original-user-input", "session-validation")

        workflow_result_constructor.assert_not_called()


def test_runner_calls_real_validator_and_returns_validated_result():
    validator = Validator()
    runner = create_runner(validator)

    with patch.object(
        validator,
        "validate",
        wraps=validator.validate,
    ) as validator_spy:
        result = runner.run("original-user-input", "session-real-validator")

    validator_spy.assert_called_once_with(
        user_input="original-user-input",
        goal="planner-goal",
        final_answer="final-answer-output",
    )
    assert result == WorkflowResult(
        user_input="original-user-input",
        goal="planner-goal",
        step_results=["step-result"],
        final_answer="final-answer-output",
        validation=ValidationResult(success=True, reasons=[]),
    )
    
