from src.agent.planning.planner import (
    Planner,
)

from src.agent.planning.models import (
    StepStatus,
)
from pydantic import ValidationError
import pytest

class FakePlannerLLM:

    def chat(
        self,
        prompt: str
    ) -> str:

        return """
{
    "goal": "制定视黄醇耐受方案",
    "steps": [
        {
            "description": "获取视黄醇信息"
        },
        {
            "description": "分析敏感肌风险"
        },
        {
            "description": "制定使用计划"
        }
    ]
}
"""


def test_planner_creates_plan():

    planner = Planner(
        llm=FakePlannerLLM()
    )

    plan = planner.create_plan(
        "制定视黄醇耐受方案"
    )

    assert (
        plan.goal
        == "制定视黄醇耐受方案"
    )

    assert len(
        plan.steps
    ) == 3


def test_planner_generates_step_ids():

    planner = Planner(
        llm=FakePlannerLLM()
    )

    plan = planner.create_plan(
        "test"
    )

    assert plan.steps[0].id == 1
    assert plan.steps[1].id == 2
    assert plan.steps[2].id == 3


def test_new_steps_are_pending():

    planner = Planner(
        llm=FakePlannerLLM()
    )

    plan = planner.create_plan(
        "test"
    )

    for step in plan.steps:

        assert (
            step.status
            == StepStatus.PENDING
        )

        assert (
            step.result is None
        )


class InvalidFakePlannerLLM:

    def chat(
        self,
        prompt: str
    ) -> str:

        return """
{
    "goal": "test",
    "steps": [
          {
                "description": "获取视黄醇信息"
            }
            ]
}
"""


def test_valid_plan():

    planner = Planner(
        llm=InvalidFakePlannerLLM()
    )

    plan = planner.create_plan(
        "test"
    )

    assert plan.goal





def test_invalid_plan_is_rejected():

    planner = Planner(
        llm=InvalidFakePlannerLLM()
    )

    with pytest.raises(
        ValidationError
    ):
        planner.create_plan(
            "test"
        )