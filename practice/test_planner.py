from src.agent.planning.planner import Planner
from src.agent.planning.models import StepStatus



class FakePlannerLLM:
    def chat(self,messages: list):
         return """
{
    "goal": "为敏感肌用户制定四周视黄醇耐受方案",
    "steps": [
        {
            "description": "了解视黄醇的基础作用和刺激风险"
        },
        {
            "description": "分析敏感肌使用视黄醇的风险"
        },
        {
            "description": "检索建立视黄醇耐受相关知识"
        },
        {
            "description": "制定四周渐进使用方案"
        },
        {
            "description": "检查方案中的刺激风险和注意事项"
        }
    ]
}
"""

def main():

    llm = FakePlannerLLM()
    planner = Planner(llm = llm)
    plan = planner.create_plan(
        """
        我是敏感肌，
        想开始用视黄醇，
        帮我制定一个四周建立耐受方案
        """
    )
    print('\nGoal: ')
    print(plan.goal)

    print('\nSteps: ')

    for step in plan.steps:

        print(step.id,step.description,step.description,step.status)

        assert (step.status == StepStatus.PENDING)

        assert (step.result is None)


if __name__ =='__main__':
    main()