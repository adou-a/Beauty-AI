from pydantic import BaseModel
from dataclasses import dataclass
@dataclass
class WorkflowResult():
    user_input: str
    goal: str
    step_results: list[str]
    final_answer: str

class ValidationResult(BaseModel):
    passed: bool
    issues: list[str]