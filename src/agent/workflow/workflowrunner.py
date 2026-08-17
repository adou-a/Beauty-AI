from src.agent.workflow.workflowstatus import WorkflowState,WorkflowStatus
from src.agent.planning.planner import Planner
from src.agent.planning.plan_executor import PlanExecutor
class WorkflowRunner:

    def __init__(self,planner:Planner,planexecutor:PlanExecutor):
        self.planner = planner
        self.plan_executor = planexecutor


    def run(self,user_input,session_id):
        
        plan = self.planner.create_plan(user_input)
        executor_context = ExecutorContext(session_id)
        workflow_state = WorkflowState()
        workflow_state.start()
        try:
            plan = self.plan_executor.execute(plan,executor_context,workflow_state)
        except Exception as exc:
            workflow_state.status = WorkflowStatus.FAILED
            workflow_state.error = str(exc)
            raise
        else:
            workflow_state.finish()
        return plan

        
        
   

class ExecutorContext:
    def __init__(self,session_id):
        self.session_id = session_id

    def executorcontext(self):

        return self.session_id

        

