from typing import Protocol
from src.agent.planning.models import Plan,PlanStep,StepStatus
from src.agent.workflow.workflowstatus import WorkflowState

class PlanStepExecutor(Protocol):

    def execute(self,step: PlanStep) -> str:
        ...

class PlanExecutionError(Exception):
    pass

#执行任务步骤，负责现在执行到那一步，状态的变化，结果放哪里
class PlanExecutor:
    def __init__(self,step_executor: PlanStepExecutor):

        self.step_executor = step_executor

    def execute(self,plan: Plan,executor_context,workflow_state:WorkflowState) -> Plan:


        for step in plan.steps:
            workflow_state.current_step_id = step.id
            #跳过已经完成步骤
            if step.status == StepStatus.COMPLETED:
                continue
            #只运行PENDING状态
            if step.status != StepStatus.PENDING:

                continue
            goal = plan.goal
            self._execute_step(step,executor_context,goal)



        return plan


    def _execute_step(self,step: PlanStep,executor_context,goal) -> None:
        step.status = StepStatus.RUNNING

        try:

            result = self.step_executor.execute(step,executor_context,goal)

        except Exception as exc:

            step.status = StepStatus.FAILED

            raise PlanExecutionError(f'plan step {step.id} failed: '
                                     f'{step.description}') from exc


        step.result = result

        step.status = StepStatus.COMPLETED

    