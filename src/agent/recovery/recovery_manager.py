from src.agent.recovery.models import RecoveryResult


class RecoveryManager:
    def __init__(self,reflection,replanner = None,final_answer = None):
        self.reflection = reflection
        self.replanner = replanner
        self.final_answer = final_answer

    def recover(self, context):

        reflection_result = (
            self.reflection.analyze(context)
        )

        if not reflection_result.need_replan:

            if self.final_answer is None:
                raise RuntimeError(
                    "FinalAnswer is required"
                )

            answer = self.final_answer.generate(
                context,
            )

            return RecoveryResult(
                recovered = True,
                final_answer = answer
            )


        if self.replanner is None:
            raise RuntimeError(
                "Replanner is required"
            )

        plan = self.replanner.plan(
            context
        )

        return RecoveryResult(
            recovered = True,
            final_answer = answer
        )

  
