from src.agent.recovery.models import RecoveryExecutionContext



class RecoveryWorkflow:

    def __init__(self,executor,final_answer):
        self.executor = executor
        self.final_answer = final_answer


    def run(self,context:RecoveryExecutionContext):
        step_results = self.executor.executor(context.plan)
        answer = self.final_answer.generate(context.use_input,step_results)

        return answer


        