from typing import Protocol
from src.agent.planning.models import PlanStep







class AgentRunner(Protocol):

    def run(self, session_id: str, user_input: str) -> str:
        ...

class AgentStepExecutionError(Exception):
    pass

class AgentStepExecutor:


    def __init__(self,agent: AgentRunner):
        self.agent = agent
       
      

    def execute(self,step: PlanStep,executor_context,goal) -> str:

        prompt = self._build_prompt(step=step,goal=goal)


        try:
            result = self.agent.run(executor_context.session_id,prompt)


        except Exception as exc:
            raise AgentStepExecutionError(f'Agent failed to execute'
                                          f'plan step {step.id}:'
                                          f'{step.description}'
                                          ) from exc


        if (not isinstance(result, str) or not result.strip()):

            raise AgentStepExecutionError(f'Agent returned empty result'
                                          f'for plan step {step.id}')



        return result.strip()


    def _build_prompt(
            self,
            step: PlanStep,
            goal
        ) -> str:

            return f"""
    你正在执行一个已经制定好的计划。

    整体目标：
    {goal}

    当前需要完成的步骤：
    {step.description}

    要求：

    只完成当前步骤。

    不要重新制定整个计划。

    你可以根据当前步骤自主决定是否使用已有工具。

    如果需要知识库资料，可以使用知识检索工具。

    如果需要业务数据，可以使用对应业务工具。

    完成后，只返回当前步骤得到的有效结果。

    不要假装其他尚未执行的步骤已经完成。
    """.strip()