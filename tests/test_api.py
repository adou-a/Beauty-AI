from fastapi.testclient import TestClient
from src.api.main import app
import httpx
import pytest
from types import SimpleNamespace
from fastapi import FastAPI
from openai import APIConnectionError, APITimeoutError, APIStatusError
from src.api.dependencies import get_gate
from src.api.main import handle_request_validation
from fastapi.exceptions import RequestValidationError
from src.agent.planning.gate import PlanningGate
from src.api.schemas import AgentRequest
from src.exceptions.rag_exception import RetrieverError


#创建一个测试客户端，导入具体文件的app
client = TestClient(app)

#测试home功能正常
def test_home():
    response = client.get('/')
    assert response.status_code == 200

#测试不存在的url
def test_not_found():
    response = client.get('/ingredients/不存在')
    assert response.status_code == 404
#可复用的依赖
@pytest.fixture
def chat_gate():
    class FakeGate:
        result = "answer"
        error = None
        calls = []

        def choice(self, *, session_id, user_input):
            self.calls.append((session_id, user_input))
            if self.error is not None:
                raise self.error
            return self.result

    fake = FakeGate()
    #复制原来依赖
    previous = app.dependency_overrides.copy()
   # 测试期间，把真实依赖换成 FakeGate
    app.dependency_overrides[get_gate] = lambda: fake
    try:
        #把 FakeGate 给测试使用
        yield fake
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.mark.parametrize("path", ["/agent/chat", "/agent/chat/"])
def test_chat_trims_contract_values(chat_gate, path):
    chat_gate.result = "  answer  "
    #以json 发给fastapi
    response = client.post(path, json={"session_id": " test-session ", "message": " 视黄醇有什么作用 "})
    assert response.status_code == 200
    #把response对象转化成python字典
    assert response.json() == {"answer": "answer"}
    assert chat_gate.calls == [("test-session", "视黄醇有什么作用")]


@pytest.mark.parametrize("decision", ["SIMPLE", "COMPLEX"])
def test_chat_real_gate_hides_routing_details(chat_gate, decision):
    calls = []

    def direct(**kwargs):
        calls.append("SIMPLE")
        return "direct answer"

    def workflow(**kwargs):
        calls.append("COMPLEX")
        return SimpleNamespace(final_answer="workflow answer", step_results=["internal"])

    gate = PlanningGate(
        llm=SimpleNamespace(chat=lambda messages: decision),
        agent=SimpleNamespace(run=direct),
        workflow_runner=SimpleNamespace(run=workflow),
    )
    app.dependency_overrides[get_gate] = lambda: gate
    response = client.post("/agent/chat/", json={"session_id": "test-session", "message": "视黄醇有什么作用"})
    assert response.status_code == 200
    assert response.json() == {"answer": "direct answer" if decision == "SIMPLE" else "workflow answer"}
    assert calls == [decision]


@pytest.mark.parametrize("field", ["session_id", "message"])
@pytest.mark.parametrize("value", [None, "", "   ", 123, True, [], {}])
@pytest.mark.parametrize("path", ["/agent/chat", "/agent/chat/"])
def test_chat_invalid_request(chat_gate, field, value, path):
    payload = {"session_id": "test-session", "message": "question"}
    payload[field] = value
    response = client.post(path, json=payload)
    assert response.status_code == 422
    assert response.json() == {"code": "invalid_request", "message": "Invalid request"}
    assert chat_gate.calls == []


# @pytest.mark.parametrize("field", ["session_id", "message"])
# def test_chat_missing_field(chat_gate, field):
#     payload = {"session_id": "test-session", "message": "question"}
#     del payload[field]
#     response = client.post("/agent/chat/", json=payload)
#     assert response.status_code == 422
#     assert response.json() == {"code": "invalid_request", "message": "Invalid request"}
#     assert chat_gate.calls == []


# @pytest.mark.parametrize("error", [
#     APIConnectionError(request=httpx.Request("POST", "https://example.invalid")),
#     APITimeoutError(request=httpx.Request("POST", "https://example.invalid")),
#     APIStatusError("private upstream error", response=httpx.Response(429, request=httpx.Request("POST", "https://example.invalid")), body=None),
# ])
# def test_chat_dependency_failure(chat_gate, error):
#     chat_gate.error = error
#     response = client.post("/agent/chat/", json={"session_id": "test-session", "message": "question"})
#     assert response.status_code == 503
#     assert response.json() == {"code": "service_unavailable", "message": "Service temporarily unavailable"}


# @pytest.mark.parametrize("error", [RuntimeError, AttributeError, TypeError, KeyError, RetrieverError])
# def test_chat_runtime_failure_is_private(chat_gate, error):
#     chat_gate.error = error("PlanningGate traceback private details")
#     response = client.post("/agent/chat/", json={"session_id": "test-session", "message": "question"})
#     assert response.status_code == 500
#     assert response.json() == {"code": "internal_error", "message": "Internal server error"}


# @pytest.mark.parametrize("answer", ["", "   ", None, 123, {"final_answer": "internal"}])
# def test_chat_invalid_answer_is_server_error(chat_gate, answer):
#     chat_gate.result = answer
#     response = client.post("/agent/chat/", json={"session_id": "test-session", "message": "question"})
#     assert response.status_code == 500
#     assert response.json() == {"code": "internal_error", "message": "Internal server error"}


# def test_other_api_keeps_default_validation_contract():
#     other_app = FastAPI()
#     other_app.add_exception_handler(RequestValidationError, handle_request_validation)

#     @other_app.post("/other")
#     def other(request: AgentRequest):
#         return request

#     response = TestClient(other_app).post("/other", json={})
#     assert response.status_code == 422
#     assert list(response.json()) == ["detail"]
#     assert {item["loc"][-1] for item in response.json()["detail"]} == {"session_id", "message"}


# def test_chat_openapi_contract():
#     operation = app.openapi()["paths"]["/agent/chat/"]["post"]
#     assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"] == "#/components/schemas/AgentRequest"
#     for status, model in [("200", "AgentResponse"), ("422", "ErrorResponse"), ("503", "ErrorResponse"), ("500", "ErrorResponse")]:
#         assert operation["responses"][status]["content"]["application/json"]["schema"]["$ref"] == f"#/components/schemas/{model}"
