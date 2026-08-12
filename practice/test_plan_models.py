from src.agent.planning.models import Plan,PlanStep,StepStatus




def main():

    plan = Plan(
        goal='为敏感肌用户制定视黄醇耐受方案',
        steps=[
            PlanStep(
                id = 1,
                description= '查询视黄醇基础信息'
            ),
            PlanStep(
                id=2,
                description='分析敏感肌使用风险'
                
            ),
            PlanStep(
                id=3,
                description='检索建立耐受相关知识'
            
            ),
        
        ]
    )
    print(plan)

    first_step = plan.steps[0]

    first_step.status = StepStatus.RUNNING

    print(first_step)

    first_step.status = StepStatus.COMPLETED

    first_step.result = ('已获得视黄醇基础资料')

    print(first_step)


if __name__ == '__main__':
    main()