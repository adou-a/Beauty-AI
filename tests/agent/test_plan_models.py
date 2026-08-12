from src.agent.planning.models import StepStatus,PlanStep,Plan

def test_plan_step_default_status():

    step = PlanStep(id=1,description='test')

    #测试最初状态
    assert(step.status == StepStatus.PENDING)



def test_plan_contains_steps():
    plan = Plan(
        goal= 'test goal',
        steps=[
            PlanStep(
                id=1,
                description='step 1'
            )
        ]
    )

    assert len(plan.steps) == 1
    assert plan.goal == 'test goal'


def test_step_can_store_result():

    step = PlanStep(
        id=1,
        description='test'
    )


    step.status = StepStatus.COMPLETED


    step.result = 'done'

    assert (step.status == StepStatus.COMPLETED)
    assert (step.result == 'done')