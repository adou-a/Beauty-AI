from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from src.api.dependencies import get_gate
from src.api.main import app


class FakeAgent:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run(self, session_id: str, user_input: str) -> str:
        self.calls.append((session_id, user_input))
        return "simple answer"


@dataclass(frozen=True)
class FakeWorkflowResult:
    final_answer: str


class FakeWorkflowRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run(self, user_input: str, session_id: str) -> FakeWorkflowResult:
        self.calls.append((user_input, session_id))
        return FakeWorkflowResult(final_answer="complex answer")


class FakePlanningGate:
    def __init__(
        self,
        decision: str,
        agent: FakeAgent,
        workflow_runner: FakeWorkflowRunner,
    ) -> None:
        self.decision = decision
        self.agent = agent
        self.workflow_runner = workflow_runner
        self.calls: list[tuple[str, str]] = []

    def choice(self, user_input: str, session_id: str) -> str:
        self.calls.append((session_id, user_input))

        if self.decision == "ERROR":
            raise RuntimeError("fake planning gate failure")
        if self.decision == "SIMPLE":
            return self.agent.run(session_id=session_id, user_input=user_input)
        if self.decision == "COMPLEX":
            result = self.workflow_runner.run(
                user_input=user_input,
                session_id=session_id,
            )
            return result.final_answer

        raise ValueError(f"unsupported fake decision: {self.decision}")


@pytest.fixture
def client() -> Iterator[TestClient]:
    original_overrides = app.dependency_overrides.copy()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def override_gate(fake_gate: FakePlanningGate) -> None:
    app.dependency_overrides[get_gate] = lambda: fake_gate


def test_api_routes_simple_request_to_agent(client: TestClient) -> None:
    agent = FakeAgent()
    workflow_runner = FakeWorkflowRunner()
    gate = FakePlanningGate("SIMPLE", agent, workflow_runner)
    override_gate(gate)

    response = client.post(
        "/agent/chat/",
        json={"session_id": "simple-session", "message": "烟酰胺有什么作用？"},
    )

    assert response.status_code == 200
    assert response.json() == {"answer": "simple answer"}
    assert gate.calls == [("simple-session", "烟酰胺有什么作用？")]
    assert agent.calls == [("simple-session", "烟酰胺有什么作用？")]
    assert workflow_runner.calls == []


def test_api_routes_complex_request_to_workflow(client: TestClient) -> None:
    agent = FakeAgent()
    workflow_runner = FakeWorkflowRunner()
    gate = FakePlanningGate("COMPLEX", agent, workflow_runner)
    override_gate(gate)

    response = client.post(
        "/agent/chat/",
        json={
            "session_id": "complex-session",
            "message": "分析视黄醇刺激原因并制定四周方案",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"answer": "complex answer"}
    assert gate.calls == [
        ("complex-session", "分析视黄醇刺激原因并制定四周方案")
    ]
    assert workflow_runner.calls == [
        ("分析视黄醇刺激原因并制定四周方案", "complex-session")
    ]
    assert agent.calls == []


def test_api_returns_500_when_planning_gate_raises(client: TestClient) -> None:
    agent = FakeAgent()
    workflow_runner = FakeWorkflowRunner()
    gate = FakePlanningGate("ERROR", agent, workflow_runner)
    override_gate(gate)

    response = client.post(
        "/agent/chat/",
        json={"session_id": "error-session", "message": "触发异常"},
    )

    assert response.status_code == 500
    assert gate.calls == [("error-session", "触发异常")]
    assert agent.calls == []
    assert workflow_runner.calls == []
