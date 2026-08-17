import pytest

from src.agent.planning.models import Plan, PlanStep
from src.agent.planning.plan_executor import PlanExecutor
from src.agent.workflow.workflowrunner import WorkflowRunner
from src.agent.workflow.workflowstatus import WorkflowStatus


class FakePlanner:
    def __init__(self, plan):
        self.plan = plan
        self.received_input = None

    def create_plan(self, user_input):
        self.received_input = user_input
        return self.plan


class FakePlanExecutor:
    def __init__(self):
        self.received_plan = None

    def execute(self, plan, executor_context, workflow_state):
        self.received_plan = plan
        plan.steps[0].result = "执行结果"
        return plan


def test_workflow_input_becomes_plan_then_executes_and_returns():
    plan = Plan(
        goal="制定护肤方案",
        steps=[PlanStep(id=1, description="分析用户需求")],
    )
    planner = FakePlanner(plan)
    executor = FakePlanExecutor()
    runner = WorkflowRunner(planner=planner, planexecutor=executor)

    result = runner.run("我的皮肤容易泛红", "session-001")

    assert planner.received_input == "我的皮肤容易泛红"
    assert executor.received_plan is plan
    assert result is plan
    assert result.steps[0].result == "执行结果"


def test_planner_failure_is_not_reported_as_success():
    class FailingPlanner:
        def create_plan(self, user_input):
            raise RuntimeError("planner failed")

    runner = WorkflowRunner(
        planner=FailingPlanner(),
        planexecutor=FakePlanExecutor(),
    )

    with pytest.raises(RuntimeError, match="planner failed"):
        runner.run("用户输入", "session-001")


def test_executor_failure_propagates_to_caller():
    plan = Plan(
        goal="制定护肤方案",
        steps=[PlanStep(id=1, description="分析用户需求")],
    )

    class FailingExecutor:
        def execute(self, plan, executor_context, workflow_state):
            raise RuntimeError("executor failed")

    runner = WorkflowRunner(
        planner=FakePlanner(plan),
        planexecutor=FailingExecutor(),
    )

    with pytest.raises(RuntimeError, match="executor failed"):
        runner.run("用户输入", "session-001")


def test_workflow_is_running_when_executor_starts():
    plan = Plan(
        goal="制定护肤方案",
        steps=[PlanStep(id=1, description="分析用户需求")],
    )

    class StatusRecordingExecutor:
        def execute(self, plan, executor_context, workflow_state):
            self.status_when_called = workflow_state.status
            return plan

    executor = StatusRecordingExecutor()
    runner = WorkflowRunner(
        planner=FakePlanner(plan),
        planexecutor=executor,
    )

    runner.run("用户输入", "session-001")

    assert executor.status_when_called == WorkflowStatus.RUNNING


def test_workflow_is_failed_after_executor_failure():
    plan = Plan(
        goal="制定护肤方案",
        steps=[PlanStep(id=1, description="分析用户需求")],
    )

    class FailingExecutor:
        def execute(self, plan, executor_context, workflow_state):
            self.workflow_state = workflow_state
            raise RuntimeError("executor failed")

    executor = FailingExecutor()
    runner = WorkflowRunner(
        planner=FakePlanner(plan),
        planexecutor=executor,
    )

    with pytest.raises(RuntimeError, match="executor failed"):
        runner.run("用户输入", "session-001")

    assert executor.workflow_state.status == WorkflowStatus.FAILED


def test_current_step_id_changes_during_plan_execution():
    plan = Plan(
        goal="制定护肤方案",
        steps=[
            PlanStep(id=1, description="分析用户需求"),
            PlanStep(id=2, description="生成护肤建议"),
        ],
    )

    class SuccessfulStepExecutor:
        def execute(self, step, executor_context, goal):
            return f"result-{step.id}"

    class CurrentStepRecordingExecutor:
        def __init__(self):
            self.delegate = PlanExecutor(SuccessfulStepExecutor())
            self.current_step_before = None
            self.current_step_after = None

        def execute(self, plan, executor_context, workflow_state):
            self.current_step_before = workflow_state.current_step_id
            result = self.delegate.execute(
                plan,
                executor_context,
                workflow_state,
            )
            self.current_step_after = workflow_state.current_step_id
            return result

    executor = CurrentStepRecordingExecutor()
    runner = WorkflowRunner(
        planner=FakePlanner(plan),
        planexecutor=executor,
    )

    runner.run("用户输入", "session-001")

    assert executor.current_step_before is None
    assert executor.current_step_after == 2
