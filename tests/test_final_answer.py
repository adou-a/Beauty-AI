import pytest

from src.agent.planning.models import Plan, PlanStep
from src.agent.workflow.final_answer import FinalAnswer
from src.agent.workflow.workflowrunner import WorkflowRunner
from src.agent.workflow.workflowstatus import WorkflowStatus


class FakeLLM:
    def __init__(self, answer="final-answer"):
        self.answer = answer
        self.messages = None

    def chat(self, messages):
        self.messages = messages
        return self.answer


class FakePlanner:
    def create_plan(self, user_input):
        return Plan(
            goal="回答用户的护肤问题",
            steps=[
                PlanStep(id=1, description="执行步骤一"),
                PlanStep(id=2, description="执行步骤二"),
            ],
        )


class FakePlanExecutor:
    def __init__(self):
        self.workflow_state = None

    def execute(self, plan, executor_context, workflow_state):
        self.workflow_state = workflow_state
        plan.steps[0].result = "step-result-1"
        plan.steps[1].result = "step-result-2"
        return plan


def create_runner(llm):
    return WorkflowRunner(
        planner=FakePlanner(),
        planexecutor=FakePlanExecutor(),
        final_answer=FinalAnswer(llm),
    )


def test_runner_answer_matches_final_answer_output():
    llm = FakeLLM(answer="这是最终综合回答")
    runner = create_runner(llm)

    answer = runner.run("请给我最终建议", "session-final-answer")

    assert answer == "这是最终综合回答"


def test_final_answer_receives_user_input_and_step_results():
    llm = FakeLLM()
    runner = create_runner(llm)
    user_input = "请分析我的护肤问题"

    runner.run(user_input, "session-final-answer")

    assert llm.messages[1] == {
        "role": "user",
        "content": user_input,
    }
    assert "step-result-1" in llm.messages[0]["content"]
    assert "step-result-2" in llm.messages[0]["content"]


def test_final_answer_error_propagates_through_runner():
    class FailingLLM:
        def __init__(self):
            self.calls = []

        def chat(self, messages):
            self.calls.append(messages)
            raise RuntimeError("final-answer failed")

    llm = FailingLLM()
    final_answer = FinalAnswer(llm)
    plan_executor = FakePlanExecutor()
    runner = WorkflowRunner(
        planner=FakePlanner(),
        planexecutor=plan_executor,
        final_answer=final_answer,
    )

    with pytest.raises(RuntimeError, match="final-answer failed"):
        runner.run("请给我最终建议", "session-final-answer")

    assert len(llm.calls) == 1
    assert llm.calls[0][1] == {
        "role": "user",
        "content": "请给我最终建议",
    }
    assert "step-result-1" in llm.calls[0][0]["content"]
    assert "step-result-2" in llm.calls[0][0]["content"]
    assert plan_executor.workflow_state.status == WorkflowStatus.FAILED
    assert plan_executor.workflow_state.error == "final-answer failed"
    assert plan_executor.workflow_state.current_step_id is None


def test_final_answer_is_not_called_when_plan_executor_fails():
    class FailingPlanExecutor:
        def execute(self, plan, executor_context, workflow_state):
            raise RuntimeError("plan executor failed")

    llm = FakeLLM()
    runner = WorkflowRunner(
        planner=FakePlanner(),
        planexecutor=FailingPlanExecutor(),
        final_answer=FinalAnswer(llm),
    )

    with pytest.raises(RuntimeError, match="plan executor failed"):
        runner.run("请给我最终建议", "session-final-answer")

    assert llm.messages is None
