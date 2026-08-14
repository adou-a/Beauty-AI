import pytest

from src.agent.planning.models import PlanStep,Plan,StepStatus
from src.agent.planning.plan_executor import PlanExecutor,PlanExecutionError


class FakeStepExecutor:
    def __init__(self):

        self.executor_steps = []


    def execute(self,step:PlanStep) -> str:


        assert step.status == StepStatus.RUNNING


        self.executor_steps.append(step.id)
        return (f'result-{step.id}')


def create_test_plan():

    return Plan(
    goal="test goal",
    steps=[
        PlanStep(
            id=1,
            description="step 1",
        ),
        PlanStep(
            id=2,
            description="step 2",
        ),
        PlanStep(
            id=3,
            description="step 3",
        ),
    ],
)

def test_plan_executor_completes_all_steps():

    plan = create_test_plan()

    fake_executor = FakeStepExecutor()

    executor = PlanExecutor(step_executor=fake_executor)


    executor.execute(plan)

    assert fake_executor.executor_steps == [1,2,3]

    for step in plan.steps:

        assert(step.status == StepStatus.COMPLETED)


def test_plan_executor_stores_results():

    plan = create_test_plan()

    executor = PlanExecutor(
        step_executor=(
            FakeStepExecutor()
        )
    )

    executor.execute(
        plan
    )

    assert (
        plan.steps[0].result
        == "result-1"
    )

    assert (
        plan.steps[1].result
        == "result-2"
    )

    assert (
        plan.steps[2].result
        == "result-3"
    )


def test_completed_step_is_skipped():

    plan = create_test_plan()

    plan.steps[0].status = (
        StepStatus.COMPLETED
    )

    plan.steps[0].result = (
        "existing-result"
    )

    fake_executor = (
        FakeStepExecutor()
    )

    executor = PlanExecutor(
        step_executor=(
            fake_executor
        )
    )

    executor.execute(
        plan
    )

    assert (
        fake_executor.executor_steps
        == [2, 3]
    )

    assert (
        plan.steps[0].result
        == "existing-result"
    )


class FailingStepExecutor:

    def execute(
        self,
        step: PlanStep,
    ) -> str:

        if step.id == 2:

            raise RuntimeError(
                "fake failure"
            )

        return (
            f"result-{step.id}"
        )

def test_failed_step_stops_plan():

    plan = create_test_plan()

    executor = PlanExecutor(
        step_executor=(
            FailingStepExecutor()
        )
    )

    with pytest.raises(
        PlanExecutionError
    ):
        executor.execute(
            plan
        )

    assert (
        plan.steps[0].status
        == StepStatus.COMPLETED
    )

    assert (
        plan.steps[1].status
        == StepStatus.FAILED
    )

    assert (
        plan.steps[2].status
        == StepStatus.PENDING
    )