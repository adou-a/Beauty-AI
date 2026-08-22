from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict

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

class ReflectionOutput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    need_replan: bool
    failure_type: Literal[
        "planning_failure",
        "execution_failure",
        "synthesis_failure",
        "unknown_failure",
    ]
    missing_information: list[str]
    reason: str





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
    



@dataclass
class ReplanResult:
    new_plan: Plan
    reason: str



@dataclass
class RecoveryExecutionContext:
    action: str
    plan: Plan
    use_input:str


