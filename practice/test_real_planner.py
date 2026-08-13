from src.ai.llm_client import (
    LLMClient,
)

from src.agent.planning.planner import (
    Planner,
)


def main():

    llm = LLMClient()

    planner = Planner(
        llm=llm
    )

    user_input = """
    我是敏感肌，
    想开始使用视黄醇，
    帮我制定一个四周建立耐受方案
    """
    

    plan = planner.create_plan(
        user_input
    )

    print(
        "\nGoal:"
    )

    print(
        plan.goal
    )

    print(
        "\nPlan:"
    )

    for step in plan.steps:

        print(
            f"{step.id}. "
            f"{step.description}"
        )

        print(
            "status:",
            step.status
        )

        print(
            "result:",
            step.result
        )


if __name__ == "__main__":
    main()