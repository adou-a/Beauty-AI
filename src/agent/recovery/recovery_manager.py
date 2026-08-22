from src.agent.recovery.models import RecoveryResult,RecoveryExecutionContext,ReflectionResult
from src.agent.recovery.models import RecoveryContext,RecoveryResult,ReplanResult
from src.agent.recovery.replanner import Replanner
from src.agent.recovery.recoveryworkflow import RecoveryWorkflow

class RecoveryManager:
    def __init__(self,reflection,replanner:Replanner,workflow:RecoveryWorkflow):
        self.reflection = reflection
        self.replanner = replanner
        self.workflow = workflow

    def recover(self, context:RecoveryContext) -> RecoveryResult:

        reflection_result = (
            self.reflection.analyze(context)
        )
        if reflection_result.need_replan:


            plan = self.replanner.replan(
                recovery_context = context,reflection_result = reflection_result
            )
            

        else:
            plan = context.old_plan
        recovery_executor_context = RecoveryExecutionContext(action = None,plan = plan,user_input = context.user_input)
        answer = self.workflow.run(recovery_executor_context)

        return RecoveryResult(recovered = True,final_answer = answer)


        
  
