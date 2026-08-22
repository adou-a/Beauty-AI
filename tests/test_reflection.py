import json

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.agent.planning.models import Plan, PlanStep, StepStatus
from src.agent.recovery.models import RecoveryContext, ReflectionResult
from src.agent.recovery.reflction import Reflection
from src.agent.validation.models import ValidationResult


class FakeLLM:
    def __init__(
        self,
        response: str = "",
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.messages: list[dict[str, str]] | None = None

    def chat(self, messages: list[dict[str, str]]) -> str:
        self.messages = messages
        if self.error is not None:
            raise self.error
        return self.response


def create_recovery_context() -> RecoveryContext:
    return RecoveryContext(
        user_input="Is this cosmetic suitable for sensitive skin?",
        goal="evaluate sensitive-skin suitability",
        old_plan=Plan(
            goal="evaluate sensitive-skin suitability",
            steps=[
                PlanStep(
                    id=1,
                    description="analyze ingredients",
                    status=StepStatus.COMPLETED,
                    result="ingredient analysis",
                )
            ],
        ),
        step_results=["ingredient analysis"],
        final_answer="The answer omitted skin suitability.",
        validation_result=ValidationResult(
            success=False,
            reasons=["missing skin suitability analysis"],
        ),
    )


def test_reflection_passes_recovery_context_and_converts_output() -> None:
    llm = FakeLLM(
        response=json.dumps(
            {
                "need_replan": False,
                "failure_type": "synthesis_failure",
                "missing_information": ["skin suitability"],
                "reason": "The execution result was not included in the answer.",
            }
        )
    )
    reflection = Reflection(llm)
    context = create_recovery_context()

    result = reflection.reflect(context)

    assert result == ReflectionResult(
        need_replan=False,
        failure_type="synthesis_failure",
        missing_information=["skin suitability"],
        reason="The execution result was not included in the answer.",
    )
    assert llm.messages is not None
    assert llm.messages[0]["role"] == "system"
    assert llm.messages[1]["role"] == "user"
    assert json.loads(llm.messages[1]["content"]) == {
        "user_input": context.user_input,
        "goal": context.goal,
        "old_plan": {
            "goal": context.old_plan.goal,
            "steps": [
                {
                    "id": 1,
                    "description": "analyze ingredients",
                    "status": "completed",
                    "result": "ingredient analysis",
                }
            ],
        },
        "step_results": context.step_results,
        "final_answer": context.final_answer,
        "validation_result": {
            "success": False,
            "reasons": ["missing skin suitability analysis"],
        },
    }


def test_reflection_propagates_invalid_structured_output() -> None:
    reflection = Reflection(
        FakeLLM(
            response=json.dumps(
                {
                    "need_replan": False,
                    "failure_type": "invalid_failure_type",
                    "missing_information": [],
                    "reason": "invalid output",
                }
            )
        )
    )

    with pytest.raises(PydanticValidationError):
        reflection.reflect(create_recovery_context())


def test_reflection_propagates_llm_error() -> None:
    llm_error = RuntimeError("reflection LLM failed")
    reflection = Reflection(FakeLLM(error=llm_error))

    with pytest.raises(RuntimeError, match="reflection LLM failed") as exc_info:
        reflection.reflect(create_recovery_context())

    assert exc_info.value is llm_error
