import pytest

from src.agent.planning.models import Plan, PlanStep, StepStatus
from src.agent.planning.plan_executor import PlanExecutor
from src.agent.recovery.models import RecoveryContext
from src.agent.validation.models import ValidationResult
from src.agent.workflow.models import WorkflowResult
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
        plan.steps[0].status = StepStatus.COMPLETED
        return plan


class FakeFinalAnswer:
    def synthesis(self, user_input, results):
        return "final-answer"


class FakeValidator:
    def validate(self, user_input, goal, final_answer):
        return ValidationResult(success=True, reasons=[])


class FakeRecoveryResult:
    success = True
    final_answer = "recovered-final-answer"


class FakeRecoveryManager:
    def __init__(self):
        self.received_context = None
        self.call_count = 0

    def recover(self, context):
        self.received_context = context
        self.call_count += 1
        return FakeRecoveryResult()


def test_workflow_input_becomes_plan_then_executes_and_returns():
    plan = Plan(
        goal="制定护肤方案",
        steps=[PlanStep(id=1, description="分析用户需求")],
    )
    planner = FakePlanner(plan)
    executor = FakePlanExecutor()
    recovery_manager = FakeRecoveryManager()
    runner = WorkflowRunner(
        planner=planner,
        planexecutor=executor,
        final_answer=FakeFinalAnswer(),
        validator=FakeValidator(),
        recovery_manager=recovery_manager,
    )

    result = runner.run("我的皮肤容易泛红", "session-001")

    assert planner.received_input == "我的皮肤容易泛红"
    assert executor.received_plan is plan
    assert isinstance(result, WorkflowResult)
    assert result.step_results == ["执行结果"]
    assert result.final_answer == "final-answer"
    assert plan.steps[0].result == "执行结果"
    assert recovery_manager.call_count == 0


def test_validation_failure_passes_recovery_context_to_recovery_manager():
    validation_result = ValidationResult(
        success=False,
        reasons=["missing risk analysis"],
    )

    class FailedValidator:
        def validate(self, user_input, goal, final_answer):
            return validation_result

    plan = Plan(
        goal="制定护肤方案",
        steps=[PlanStep(id=1, description="分析用户需求")],
    )
    recovery_manager = FakeRecoveryManager()
    runner = WorkflowRunner(
        planner=FakePlanner(plan),
        planexecutor=FakePlanExecutor(),
        final_answer=FakeFinalAnswer(),
        validator=FailedValidator(),
        recovery_manager=recovery_manager,
    )

    runner.run("我的皮肤容易泛红", "session-recovery")

    assert recovery_manager.call_count == 1
    context = recovery_manager.received_context
    assert isinstance(context, RecoveryContext)
    assert context.user_input == "我的皮肤容易泛红"
    assert context.goal == plan.goal
    assert context.old_plan is plan
    assert context.step_results == ["执行结果"]
    assert context.final_answer == "final-answer"
    assert context.validation_result is validation_result


def test_planner_failure_is_not_reported_as_success():
    class FailingPlanner:
        def create_plan(self, user_input):
            raise RuntimeError("planner failed")

    runner = WorkflowRunner(
        planner=FailingPlanner(),
        planexecutor=FakePlanExecutor(),
        final_answer=FakeFinalAnswer(),
        validator=FakeValidator(),
        recovery_manager=FakeRecoveryManager(),
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
        final_answer=FakeFinalAnswer(),
        validator=FakeValidator(),
        recovery_manager=FakeRecoveryManager(),
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
            plan.steps[0].status = StepStatus.COMPLETED
            return plan

    executor = StatusRecordingExecutor()
    runner = WorkflowRunner(
        planner=FakePlanner(plan),
        planexecutor=executor,
        final_answer=FakeFinalAnswer(),
        validator=FakeValidator(),
        recovery_manager=FakeRecoveryManager(),
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
        final_answer=FakeFinalAnswer(),
        validator=FakeValidator(),
        recovery_manager=FakeRecoveryManager(),
    )

    with pytest.raises(RuntimeError, match="executor failed"):
        runner.run("用户输入", "session-001")

    assert executor.workflow_state.status == WorkflowStatus.FAILED


def test_workflow_fails_when_any_step_is_not_completed():
    plan = Plan(
        goal="制定护肤方案",
        steps=[
            PlanStep(id=1, description="分析用户需求", status=StepStatus.COMPLETED),
            PlanStep(id=2, description="生成护肤建议", status=StepStatus.FAILED),
            PlanStep(id=3, description="检查最终方案", status=StepStatus.PENDING),
        ],
    )

    class IncompletePlanExecutor:
        def execute(self, plan, executor_context, workflow_state):
            self.workflow_state = workflow_state
            return plan

    class RecordingFinalAnswer:
        def __init__(self):
            self.called = False

        def synthesis(self, user_input, results):
            self.called = True
            return "final-answer"

    class RecordingValidator:
        def __init__(self):
            self.called = False

        def validate(self, user_input, goal, final_answer):
            self.called = True
            return ValidationResult(success=True, reasons=[])

    executor = IncompletePlanExecutor()
    final_answer = RecordingFinalAnswer()
    validator = RecordingValidator()
    runner = WorkflowRunner(
        planner=FakePlanner(plan),
        planexecutor=executor,
        final_answer=final_answer,
        validator=validator,
        recovery_manager=FakeRecoveryManager(),
    )

    with pytest.raises(RuntimeError, match="not all plan steps are completed"):
        runner.run("用户输入", "session-incomplete")

    assert executor.workflow_state.status == WorkflowStatus.FAILED
    assert final_answer.called is False
    assert validator.called is False


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
        final_answer=FakeFinalAnswer(),
        validator=FakeValidator(),
        recovery_manager=FakeRecoveryManager(),
    )

    runner.run("用户输入", "session-001")

    assert executor.current_step_before is None
    assert executor.current_step_after == 2
