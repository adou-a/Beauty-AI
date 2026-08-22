import json

from src.agent.recovery.models import (
    RecoveryContext,
    ReflectionOutput,
    ReflectionResult,
)
from src.ai.llm_client import LLMClient


class Reflection:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def reflect(
        self,
        recovery_context: RecoveryContext,
    ) -> ReflectionResult:
        messages = self._build_messages(recovery_context)
        response = self.llm.chat(messages)
        content = self._get_content(response)
        output = ReflectionOutput.model_validate_json(content)

        return ReflectionResult(
            need_replan=output.need_replan,
            failure_type=output.failure_type,
            missing_information=output.missing_information,
            reason=output.reason,
        )

    def analyze(
        self,
        recovery_context: RecoveryContext,
    ) -> ReflectionResult:
        """Keep compatibility with the existing RecoveryManager contract."""
        return self.reflect(recovery_context)

    def _build_messages(
        self,
        recovery_context: RecoveryContext,
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": self._build_prompt(),
            },
            {
                "role": "user",
                "content": json.dumps(
                    self._serialize_context(recovery_context),
                    ensure_ascii=False,
                ),
            },
        ]

    def _serialize_context(
        self,
        recovery_context: RecoveryContext,
    ) -> dict[str, object]:
        return {
            "user_input": recovery_context.user_input,
            "goal": recovery_context.goal,
            "old_plan": {
                "goal": recovery_context.old_plan.goal,
                "steps": [
                    {
                        "id": step.id,
                        "description": step.description,
                        "status": step.status.value,
                        "result": step.result,
                    }
                    for step in recovery_context.old_plan.steps
                ],
            },
            "step_results": recovery_context.step_results,
            "final_answer": recovery_context.final_answer,
            "validation_result": recovery_context.validation_result.model_dump(),
        }

    def _get_content(self, response: object) -> str:
        if isinstance(response, str):
            content = response
        else:
            content = getattr(response, "content", None)

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Reflection received an empty LLM response")

        return content

    def _build_prompt(self) -> str:
        output_schema = json.dumps(
            ReflectionOutput.model_json_schema(),
            ensure_ascii=False,
        )
        return f"""
你是 Beauty-AI 的 Workflow Failure Analyst。

你只负责分析 Validation Failure 的原因、判断失败类型，以及判断是否需要重新规划。

输入是一个完整的 RecoveryContext，包含：
- user_input：用户原始输入
- goal：用户目标
- old_plan：旧 Plan
- step_results：旧 Plan 的执行结果
- final_answer：验证失败的最终答案
- validation_result：Validator 结果及 failure reasons

必须按照以下流程分析：
1. 查看用户目标。
2. 查看最终答案。
3. 查看 Validator failure reasons。
4. 对比旧 Plan 和执行结果。
5. 判断 failure_type。
6. 判断 need_replan。

failure_type 只能是：
- planning_failure：旧 Plan 未覆盖用户目标所需的必要分析。
- execution_failure：旧 Plan 合理，但执行结果缺失或执行未到位。
- synthesis_failure：执行结果已包含所需信息，但最终答案未正确整合。
- unknown_failure：现有上下文不足以归入以上类型。

禁止：
- 生成新的用户答案。
- 提出新的执行步骤。
- 修改旧计划。
- 直接生成新的 Plan。
- 执行 Tool。
- 判断回答中事实的正确性。

只能返回符合 ReflectionOutput schema 的合法 JSON，不要返回 Markdown 代码块或其他文字。
ReflectionOutput JSON Schema：
{output_schema}
""".strip()
