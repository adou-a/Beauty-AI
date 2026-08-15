from src.agent.planning.models import Plan, PlanStep
from src.agent.workflow.workflowstatus import WorkflowState, WorkflowStatus


plan = Plan(
    goal="制定视黄醇耐受方案",
    steps=[
        PlanStep(
            id=1,
            description="获取视黄醇信息",
        ),
        PlanStep(
            id=2,
            description="分析敏感肌风险",
        ),
        PlanStep(
            id=3,
            description="制定使用建议",
        ),
    ],
)


def create_workflow():
    step_ids = [step.id for step in plan.steps]
    return WorkflowState(step_ids)


def test_workflow_state_starts_pending():
    workflow = create_workflow()

    assert workflow.status == WorkflowStatus.PENDING


def test_workflow_state_has_no_current_step_initially():
    workflow = create_workflow()

    assert workflow.current_step_id is None


def test_workflow_state_has_no_error_initially():
    workflow = create_workflow()

    assert workflow.error is None

