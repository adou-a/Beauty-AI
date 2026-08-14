from src.agent.planning.models import Plan,PlanStep

from src.agent.planning.plan_executor import PlanExecutor

class FakeStepExecutor:

    def execute(self,step: PlanStep) -> str:

        print(f'\nExecuting step'
              f'{step.id}'
              f'{step.description}'
              )

        print('status during execution', step.status)


        return (f'完成: {step.description}')



def main():
    plan = Plan(
        goal= '指定视黄醇耐受方案',
        steps=[
            PlanStep(id=1,description='获取视黄醇基础信息'),
            PlanStep(id=2,description='分析敏感肌风险'),
            PlanStep(id=3,description='指定四周使用方案')
        ]
    )

    executor = PlanExecutor(step_executor=FakeStepExecutor())


    executor.execute(plan)


    print('\nFinal Plan') 

    for step in plan.steps:
        print(step.id,step.description,step.status,step.result)


if __name__ == '__main__':
    main()