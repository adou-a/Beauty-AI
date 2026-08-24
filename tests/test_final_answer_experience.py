from unittest.mock import Mock

from src.agent.workflow.final_answer import FinalAnswer


INTERNAL_KEYWORDS = ("step", "planner", "agent", "tool", "rag")
MAX_ANSWER_LENGTH = 300


def create_final_answer(llm_output: str) -> tuple[FinalAnswer, Mock]:
    llm = Mock()
    llm.chat.return_value = llm_output
    return FinalAnswer(llm=llm), llm


def assert_no_internal_workflow_terms(answer: str) -> None:
    normalized_answer = answer.casefold()
    for keyword in INTERNAL_KEYWORDS:
        assert keyword not in normalized_answer


def test_complex_question_returns_integrated_user_facing_answer() -> None:
    step_results = [
        "肤质分析：用户为敏感性混合肌，面颊容易泛红。",
        "成分查询：烟酰胺有助于改善肤色，但需要从低浓度开始。",
        "风险分析：高浓度烟酰胺可能增加刺痛和泛红风险。",
        "使用建议：先局部试用，晚间隔天使用，并配合保湿。",
    ]
    user_input = "请结合我的肤质、成分风险和使用方式给出完整建议。"
    llm_output = (
        "你属于容易泛红的敏感性混合肌，使用烟酰胺时建议从低浓度开始。"
        "首次使用前先进行局部测试，确认没有明显刺痛或泛红后，再于晚间隔天使用，"
        "同时做好保湿；如果不适持续，应暂停使用。"
    )
    final_answer, llm = create_final_answer(llm_output)

    answer = final_answer.synthesis(step_results, user_input)

    assert isinstance(answer, str)
    assert answer.strip()
    assert_no_internal_workflow_terms(answer)
    assert "建议" in answer
    assert "执行日志" not in answer

    messages = llm.chat.call_args.args[0]
    assert messages[1] == {"role": "user", "content": user_input}
    for step_result in step_results:
        assert step_result in messages[0]["content"]


def test_internal_execution_information_is_not_exposed() -> None:
    step_results = [
        "StepExecutor failed",
        "Planner generated step",
        "Tool call result",
        "可用结论：当前产品不适合继续使用，建议暂停并观察皮肤状态。",
    ]
    user_input = "我还应该继续使用这个产品吗？"
    llm_output = "目前不建议继续使用。请先暂停并观察皮肤状态，待不适缓解后再评估。"
    final_answer, llm = create_final_answer(llm_output)

    answer = final_answer.synthesis(step_results, user_input)

    assert isinstance(answer, str)
    assert answer.strip()
    assert_no_internal_workflow_terms(answer)
    for internal_text in step_results[:3]:
        assert internal_text not in answer

    system_prompt = llm.chat.call_args.args[0][0]["content"]
    for internal_text in step_results[:3]:
        assert internal_text in system_prompt


def test_skincare_plan_has_readable_plain_text_format() -> None:
    step_results = [
        "早间：温和洁面、保湿、防晒。",
        "晚间：温和洁面、保湿，视黄醇每周使用两次。",
        "出现持续刺痛、脱皮或泛红时暂停视黄醇。",
    ]
    user_input = "请为刚开始使用视黄醇的敏感肌制定护肤方案。"
    llm_output = (
        "早间使用温和洁面产品，随后保湿并做好防晒。"
        "晚间清洁后先保湿，视黄醇从每周两次开始，避免连续使用。"
        "如果出现持续刺痛、脱皮或泛红，请暂停视黄醇并观察皮肤状态。"
    )
    final_answer, _ = create_final_answer(llm_output)

    answer = final_answer.synthesis(step_results, user_input)

    assert isinstance(answer, str)
    assert answer.strip()
    assert len(answer) <= MAX_ANSWER_LENGTH
    assert "#" not in answer
    assert "**" not in answer
    assert "早间" in answer
    assert "晚间" in answer
    assert "视黄醇" in answer
