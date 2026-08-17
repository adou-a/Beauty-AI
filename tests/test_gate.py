from src.agent.planning.gate import PlanningGate
from src.ai.llm_client import LLMClient


def classify(user_input):
    gate = PlanningGate(
        llm=LLMClient(),
        agent=None,
        workflow_runner=None,
    )
    messages = gate._build_messages(user_input)
    response = gate.llm.chat(messages)
    return gate._get_decision(response)


def test_simple_query_outputs_simple():
    assert classify("烟酰胺是什么？") == "SIMPLE"


def test_complex_query_outputs_complex():
    user_input = """我是敏感肌，
使用视黄醇后刺痛，
帮我分析原因并制定四周调整方案"""

    assert classify(user_input) == "COMPLEX"
