from src.agent.recovery.models import RecoveryContext, ReflectionResult, ReplanResult


class Replanner:

    def __init__(self):
        ...

    def replan(
        self,
        recovery_context: RecoveryContext,
        reflection_result: ReflectionResult,
    ) -> ReplanResult:
        ...


        
        
