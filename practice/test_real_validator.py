from dataclasses import dataclass

from src.agent.validation.validator import Validator
from src.ai.llm_client import LLMClient


USER_INPUT = "分析视黄醇作用、敏感肌风险、使用建议"
GOAL = "完整回答视黄醇的作用、敏感肌使用风险和使用建议"


@dataclass(frozen=True)
class ValidationCase:
    name: str
    answer: str
    expected_success: bool
    expected_reasons: list[str] | None = None


CASES = [
    ValidationCase(
        name="Case 1：完整回答",
        answer="""
作用：视黄醇能促进表皮更新，并有助于改善细纹、痘痘和肤色不均。

敏感肌风险：可能出现干燥、脱皮、刺痛、泛红等刺激反应；敏感肌更容易不耐受。

使用建议：先做局部测试，从低浓度、每周一至两次、夜间少量使用开始，耐受后再逐渐增加频率。配合保湿，白天注意防晒；出现持续或明显刺激时停用并咨询专业人士。
""".strip(),
        expected_success=True,
        expected_reasons=[],
    ),
    ValidationCase(
        name="Case 2：缺失部分",
        answer="视黄醇能促进表皮更新，并有助于改善细纹、痘痘和肤色不均。",
        expected_success=False,
        expected_reasons=["未提供敏感肌风险", "未提供使用建议"],
    ),
    ValidationCase(
        name="Case 3：只提关键词",
        answer="视黄醇可以改善皮肤问题。",
        expected_success=False,
    ),
    ValidationCase(
        name="Case 4：回答正确但不完全（最低充分完成）",
        answer=(
            "视黄醇可促进皮肤更新、改善细纹和痘痘；敏感肌使用时可能泛红、"
            "干燥或刺痛。建议从低浓度、低频率开始，先局部测试，同时保湿并在白天防晒。"
        ),
        # 三项要求均已得到最低限度的实质回答，预期应通过。
        expected_success=True,
        expected_reasons=[],
    ),
]


def main() -> None:
    # 使用项目真实的 LLM 客户端和 Validator，不使用 fake 或 mock。
    validator = Validator(llm=LLMClient())

    for case in CASES:
        result = validator.validate(
            user_input=USER_INPUT,
            goal=GOAL,
            final_answer=case.answer,
        )

        print(f"\n{'=' * 20} {case.name} {'=' * 20}")
        print(f"answer: {case.answer}")
        print(
            "expected:",
            {
                "success": case.expected_success,
                "reasons": case.expected_reasons,
            },
        )
        print(
            "actual:  ",
            {
                "success": result.success,
                "reasons": result.reasons,
            },
        )


if __name__ == "__main__":
    main()
