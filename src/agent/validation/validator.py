from src.agent.validation.models import ValidationOutput, ValidationResult
from src.agent.validation.prompts import ANSWER_VALITOR_PROMPT
from src.ai.llm_client import LLMClient


class ValidationError(ValueError):
    """The validator returned a structurally valid but contradictory result."""


class Validator:

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def validate(
        self,
        user_input: str,
        goal: str,
        final_answer: str,
    ) -> ValidationResult:
        if not user_input.strip():
            raise ValueError("user_input cannot be empty")
        if not goal.strip():
            raise ValueError("goal cannot be empty")
        if not final_answer.strip():
            raise ValueError("final_answer cannot be empty")

        message = self._build_prompt()
        messages = [
            {
                "role": "system",
                "content": message,
            },
            {
                "role": "user",
                'content':f'''
user_input:{user_input}
goal: {goal}
final_answer: {final_answer}

'''
            },
        ]

        response = self.llm.chat(messages)
        content = self._get_content(response)
        output = ValidationOutput.model_validate_json(content)

        if output.success and output.reasons:
            raise ValidationError(
                "Validator returned reasons for a successful validation"
            )

        return ValidationResult(
            success=output.success,
            reasons=output.reasons,
        )

    def _get_content(self, response) -> str:
        if isinstance(response, str):
            content = response
        else:
            content = getattr(response, "content", None)

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Validator received an empty LLM response")

        return content

    def _build_prompt(self) -> str:
        return f"""
{ANSWER_VALITOR_PROMPT}



只返回合法 JSON,不要使用 Markdown 代码块。

校验通过时返回：
{{
  "success": true,
  "reasons": []
}}

校验不通过时返回：
{{
  "success": false,
  "reasons": ["没有满足要求的具体原因"]
}}

success 可以是 true 或 false。
当 success 为 true 时,reasons 必须为空列表。
当 success 为 false 时，在 reasons 中说明未通过原因。
""".strip()
