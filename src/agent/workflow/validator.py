from src.agent.workflow.models import ValidationResult


class  Validator:

    def __init__(self):
        pass

    def validate(self,user_input: str,goal: str,final_answer: str)-> ValidationResult:
        return ValidationResult(
            success=True,
            reasons=[]
        )

        
