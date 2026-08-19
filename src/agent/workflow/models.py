from src.agent.validation.models import ValidationResult
from dataclasses import dataclass



@dataclass
class WorkflowResult():
    user_input: str
    goal: str
    step_results: list[str]
    final_answer: str
    validation: ValidationResult

