from pydantic import BaseModel
from dataclasses import dataclass
class ValidationResult(BaseModel):
    success: bool
    reasons: list[str]


@dataclass
class WorkflowResult():
    user_input: str
    goal: str
    step_results: list[str]
    final_answer: str
    validation:ValidationResult

