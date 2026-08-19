from src.agent.workflow.workflowstatus import WorkflowState,WorkflowStatus
from src.agent.planning.planner import Planner
from src.agent.planning.plan_executor import PlanExecutor
from src.agent.workflow.final_answer import FinalAnswer
from src.agent.workflow.models import WorkflowResult
class WorkflowRunner:

    def __init__(self,planner:Planner,planexecutor:PlanExecutor,final_answer:FinalAnswer):
        self.planner = planner
        self.plan_executor = planexecutor
        self.final_answer = final_answer

    def run(self,user_input,session_id) -> WorkflowResult:
        
        plan = self.planner.create_plan(user_input)
        executor_context = ExecutorContext(session_id)
        workflow_state = WorkflowState()
        workflow_state.start()
        try:
            executed_plan = self.plan_executor.execute(plan,executor_context,workflow_state)

            results = []
            for step in executed_plan.steps:
                if step.result is not None:
                    results.append(step.result)

            answer = self.final_answer.synthesis(
                user_input=user_input,
                results=results,
            )
        except Exception as exc:
            workflow_state.status = WorkflowStatus.FAILED
            workflow_state.error = str(exc)
            raise

        workflow_state.finish()
        return WorkflowResult(user_input = user_input,goal = plan.goal,final_answer = answer,step_results = results)
       
        
        
   

class ExecutorContext:
    def __init__(self,session_id):
        self.session_id = session_id

    def executorcontext(self):

        return self.session_id

        

