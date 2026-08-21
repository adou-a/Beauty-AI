from dataclasses import dataclass
from src.agent.planning.models import Plan
from src.agent.validation.models import ValidationResult
@dataclass
class RecoveryContext:
    user_input: str
    goal: str
    old_plan: Plan
    step_results : list[str]
    final_answer: str
    validation_result: ValidationResult




@dataclass
class ReflectionResult:
    need_replan: bool
    failure_type: str
    missing_information: list[str]
    reason: str


@dataclass
class RecoveryResult:
    recovered: bool
    final_answer : str | None
    


