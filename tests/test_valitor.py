from unittest.mock import patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.agent.planning.models import Plan, PlanStep
from src.agent.workflow.models import  WorkflowResult
from src.agent.validation.validator import ValidationError, Validator
from src.agent.workflow.workflowrunner import WorkflowRunner
from src.agent.validation.models import ValidationResult


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
    class ValidatorLLM:
        def chat(self, messages):
            return '{"success": true, "reasons": []}'

    validator = Validator(ValidatorLLM())
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


def test_validator_rejects_reasons_when_success_is_true():
    class InconsistentValidatorLLM:
        def chat(self, messages):
            return """{
                "success": true,
                "reasons": ["unexpected reason"]
            }"""

    validator = Validator(InconsistentValidatorLLM())

    with pytest.raises(
        ValidationError,
        match="reasons for a successful validation",
    ):
        validator.validate(
            user_input="original-user-input",
            goal="planner-goal",
            final_answer="final-answer-output",
        )


def test_validator_converts_llm_json_to_validation_result():
    class JsonValidationLLM:
        def chat(self, messages):
            return """{
                "success": false,
                "reasons": ["missing risk analysis"]
            }"""

    validator = Validator(JsonValidationLLM())

    result = validator.validate(
        user_input="original-user-input",
        goal="planner-goal",
        final_answer="final-answer-output",
    )

    assert isinstance(result, ValidationResult)
    assert result.success is False
    assert result.reasons == ["missing risk analysis"]


def test_validator_passes_complete_data_contract_to_llm():
    class RecordingFakeLLM:
        def __init__(self):
            self.messages = None

        def chat(self, messages):
            self.messages = messages
            return '{"success": true, "reasons": []}'

    llm = RecordingFakeLLM()
    validator = Validator(llm)

    validator.validate(
        user_input="original-user-input",
        goal="planner-goal",
        final_answer="final-answer-output",
    )

    assert llm.messages is not None
    assert llm.messages[1]["role"] == "user"

    content = llm.messages[1]["content"]
    assert "original-user-input" in content
    assert "planner-goal" in content
    assert "final-answer-output" in content


def test_validator_rejects_invalid_llm_output_structure():
    class InvalidOutputLLM:
        def chat(self, messages):
            return "这个答案没有完成目标"

    validator = Validator(InvalidOutputLLM())

    with pytest.raises(PydanticValidationError):
        validator.validate(
            user_input="original-user-input",
            goal="planner-goal",
            final_answer="final-answer-output",
        )


def test_llm_failure_propagates_through_validator():
    class FailingLLM:
        def chat(self, messages):
            raise RuntimeError("LLM failed")

    validator = Validator(FailingLLM())

    with pytest.raises(RuntimeError, match="LLM failed"):
        validator.validate(
            user_input="original-user-input",
            goal="planner-goal",
            final_answer="final-answer-output",
        )

def test_validator_rejects_string_instead_of_boolean():
    class StringBooleanLLM:
        def chat(self, messages):
            return '{"success": "yes", "reasons": []}'

    validator = Validator(StringBooleanLLM())

    with pytest.raises(PydanticValidationError):
        validator.validate(
            user_input="original-user-input",
            goal="planner-goal",
            final_answer="final-answer-output",
        )


def test_validator_rejects_unexpected_fields():
    class ExtraFieldLLM:
        def chat(self, messages):
            return """{
                "success": false,
                "reasons": ["缺少风险"],
                "confidence": 0.8
            }"""

    validator = Validator(ExtraFieldLLM())

    with pytest.raises(PydanticValidationError):
        validator.validate(
            user_input="original-user-input",
            goal="planner-goal",
            final_answer="final-answer-output",
        )
