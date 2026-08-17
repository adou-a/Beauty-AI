from typing import Protocol

from src.utils.logger import get_logger


logger = get_logger(__name__)


CHOICE_SUITABEL_PROMPT = """
你是 Beauty-AI 的任务复杂度判断器。

请根据用户问题判断应该直接交给 Agent 处理，还是进入规划工作流。

SIMPLE:
- 目标单一、要求明确
- 不需要拆分为多个相互依赖的步骤
- 通常一次回答或一次工具调用即可完成

COMPLEX:
- 目标复杂，需要先制定计划
- 需要多个有先后关系的步骤
- 可能需要多次调用工具并综合结果

只能输出以下一个值：
SIMPLE
COMPLEX
""".strip()


class GateLLM(Protocol):
    def chat(self, messages: list[dict[str, str]]):
        ...


class DirectAgent(Protocol):
    def run(self, session_id: str, user_input: str) -> str:
        ...


class WorkflowRunnerProtocol(Protocol):
    def run(self, user_input: str, session_id: str):
        ...


class PlanningGate:
    def __init__(
        self,
        llm: GateLLM,
        agent: DirectAgent,
        workflow_runner: WorkflowRunnerProtocol,
    ):
        self.llm = llm
        self.agent = agent
        self.workflow_runner = workflow_runner

    def choice(self, user_input: str, session_id: str):
        logger.info(
            "Planning gate received request session=%s",
            session_id,
        )

        messages = self._build_messages(user_input)
        try:
            logger.info(
                "Planning gate classifying request session=%s",
                session_id,
            )
            response = self.llm.chat(messages)
            decision = self._get_decision(response)
        except Exception:
            logger.exception(
                "Planning gate classification failed session=%s",
                session_id,
            )
            raise

        logger.info(
            "Planning gate decision=%s session=%s",
            decision,
            session_id,
        )

        if decision == "SIMPLE":
            logger.info(
                "Planning gate routing to direct agent session=%s",
                session_id,
            )
            return self.agent.run(
                session_id=session_id,
                user_input=user_input,
            )

        logger.info(
            "Planning gate routing to workflow runner session=%s",
            session_id,
        )
        return self.workflow_runner.run(
            user_input=user_input,
            session_id=session_id,
        )

    def _build_messages(self, user_input: str) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": CHOICE_SUITABEL_PROMPT,
            },
            {
                "role": "user",
                "content": user_input,
            },
        ]

    def _get_decision(self, response) -> str:
        if isinstance(response, str):
            content = response
        else:
            content = getattr(response, "content", None)

        if not isinstance(content, str) or not content.strip():
            logger.warning("Planning gate received empty LLM response")
            raise ValueError("PlanningGate received an empty LLM response")

        decision = content.strip().upper()
        if decision not in {"SIMPLE", "COMPLEX"}:
            logger.warning("Planning gate received invalid LLM decision")
            raise ValueError(
                f"PlanningGate received an invalid decision: {content!r}"
            )

        return decision
