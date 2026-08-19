from unittest.mock import patch

import pytest

from src.agent.planning.models import Plan, PlanStep
from src.agent.workflow.models import WorkflowResult
from src.agent.workflow.workflowrunner import WorkflowRunner


class FakePlanner:
    def __init__(self):
        self.plan = Plan(
            goal="planner-goal",
            steps=[
                PlanStep(id=1, description="step-1"),
                PlanStep(id=2, description="step-2"),
            ],
        )
        self.received_input = None

    def create_plan(self, user_input):
        self.received_input = user_input
        return self.plan


class FakePlanExecutor:
    def __init__(self):
        self.returned_results = ["executor-result-1", "executor-result-2"]

    def execute(self, plan, executor_context, workflow_state):
        for step, result in zip(plan.steps, self.returned_results):
            step.result = result
        return plan


class FakeFinalAnswer:
    def __init__(self):
        self.returned_answer = "final-answer-result"
        self.received_user_input = None
        self.received_results = None

    def synthesis(self, user_input, results):
        self.received_user_input = user_input
        self.received_results = results
        return self.returned_answer


def create_runner():
    planner = FakePlanner()
    executor = FakePlanExecutor()
    final_answer = FakeFinalAnswer()
    runner = WorkflowRunner(
        planner=planner,
        planexecutor=executor,
        final_answer=final_answer,
    )
    return runner, planner, executor, final_answer


def test_workflow_runner_creates_workflow_result():
    runner, _, _, _ = create_runner()

    result = runner.run("original-user-input", "session-workresult")

    assert isinstance(result, WorkflowResult)
    assert result == WorkflowResult(
        user_input="original-user-input",
        goal="planner-goal",
        step_results=["executor-result-1", "executor-result-2"],
        final_answer="final-answer-result",
    )


def test_workflow_result_fields_come_from_correct_modules():
    runner, planner, executor, final_answer = create_runner()
    user_input = "original-user-input"

    result = runner.run(user_input, "session-workresult")

    assert result.user_input == user_input
    assert result.goal == planner.plan.goal
    assert result.step_results == executor.returned_results
    assert result.final_answer == final_answer.returned_answer
    assert planner.received_input == user_input
    assert final_answer.received_user_input == user_input
    assert final_answer.received_results == executor.returned_results


def test_planner_or_executor_failure_does_not_create_fake_workflow_result():
    class FailingPlanner:
        def create_plan(self, user_input):
            raise RuntimeError("planner failed")

    class FailingExecutor:
        def execute(self, plan, executor_context, workflow_state):
            raise RuntimeError("executor failed")

    final_answer = FakeFinalAnswer()

    with patch(
        "src.agent.workflow.workflowrunner.WorkflowResult"
    ) as workflow_result_constructor:
        planner_failure_runner = WorkflowRunner(
            planner=FailingPlanner(),
            planexecutor=FakePlanExecutor(),
            final_answer=final_answer,
        )
        with pytest.raises(RuntimeError, match="planner failed"):
            planner_failure_runner.run("user-input", "session-planner-failure")

        executor_failure_runner = WorkflowRunner(
            planner=FakePlanner(),
            planexecutor=FailingExecutor(),
            final_answer=final_answer,
        )
        with pytest.raises(RuntimeError, match="executor failed"):
            executor_failure_runner.run("user-input", "session-executor-failure")

        workflow_result_constructor.assert_not_called()

    assert final_answer.received_user_input is None
    assert final_answer.received_results is None
