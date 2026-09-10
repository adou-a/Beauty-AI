import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APIConnectionError, APIStatusError, APITimeoutError

from src.api import main as api_main
from src.api.dependencies import get_gate
from src.api.main import app
from src.config import settings
from src.rag.vector_store import VectorStore


INTERNAL_ERROR = {
    "code": "internal_error",
    "message": "Internal server error",
}
SERVICE_UNAVAILABLE = {
    "code": "service_unavailable",
    "message": "Service temporarily unavailable",
}


INVALID_INDEX_PAYLOADS = [
    ("broken-json", "{\"fact\":"),
    ("empty-index", "[]"),
]


@pytest.fixture(autouse=True)
def restore_dependency_overrides(monkeypatch: pytest.MonkeyPatch):
    previous = app.dependency_overrides.copy()
    monkeypatch.setattr(
        settings,
        "DEEPSEEK_API_KEY",
        "test-deepseek-api-key",
    )
    try:
        yield
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)

#把本来vector换成测试的vector
def use_startup_vector_store(
    monkeypatch: pytest.MonkeyPatch,
    storage_path: Path,
) -> None:
    monkeypatch.setattr(
        api_main,
        "VectorStore",
        lambda: VectorStore(storage_path=str(storage_path)),
        raising=False,
    )


def use_available_startup_vector_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class AvailableVectorStore:
        def load_required(self) -> None:
            return None

    monkeypatch.setattr(api_main, "VectorStore", AvailableVectorStore)


def test_app_startup_fails_when_deepseek_api_key_is_missing(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", None)
    use_available_startup_vector_store(monkeypatch)

    with pytest.raises(
        RuntimeError,
        match="DEEPSEEK_API_KEY startup validation failed",
    ):
        with TestClient(app):
            pass


@pytest.mark.parametrize(
    "api_key",
    ["", " \t\r\n"],
    ids=["empty", "whitespace-only"],
)
def test_app_startup_fails_when_deepseek_api_key_is_blank(
    api_key: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", api_key)
    use_available_startup_vector_store(monkeypatch)

    with pytest.raises(
        RuntimeError,
        match="DEEPSEEK_API_KEY startup validation failed",
    ):
        with TestClient(app):
            pass


def test_app_startup_accepts_non_empty_deepseek_api_key(
    monkeypatch: pytest.MonkeyPatch,
):
    load_calls = []

    class RecordingVectorStore:
        def load_required(self) -> None:
            load_calls.append("load_required")

    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "fake-key")
    monkeypatch.setattr(api_main, "VectorStore", RecordingVectorStore)

    with TestClient(app) as startup_client:
        response = startup_client.get("/")

    assert response.status_code == 200
    assert load_calls == ["load_required"]


def test_app_startup_fails_when_vector_store_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    use_startup_vector_store(monkeypatch, tmp_path / "missing.json")

    with pytest.raises(
        RuntimeError,
        match="Vector store startup validation failed",
    ):
        with TestClient(app):
            pass


@pytest.mark.parametrize(
    ("case_name", "payload"),
    INVALID_INDEX_PAYLOADS,
    ids=[case[0] for case in INVALID_INDEX_PAYLOADS],
)
def test_app_startup_fails_when_vector_store_is_invalid(
    case_name: str,
    payload: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    storage_path = tmp_path / f"{case_name}.json"
    storage_path.write_text(payload, encoding="utf-8")
    use_startup_vector_store(monkeypatch, storage_path)

    with pytest.raises(
        RuntimeError,
        match="Vector store startup validation failed",
    ):
        with TestClient(app):
            pass


def test_app_startup_accepts_release_29_fact_index(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    release_path = Path(__file__).resolve().parents[1] / "data" / "vector_store.json"
    release_payload = release_path.read_text(encoding="utf-8")
    assert len(json.loads(release_payload)) == 29

    storage_path = tmp_path / "vector_store.json"
    storage_path.write_text(release_payload, encoding="utf-8")
    use_startup_vector_store(monkeypatch, storage_path)

    with TestClient(app) as startup_client:
        response = startup_client.get("/")

    assert response.status_code == 200

#依赖构造阶段的错误
def test_unhandled_dependency_exception_returns_private_json_500():
    def broken_dependency():
        raise KeyError("private dependency path and secret")

    app.dependency_overrides[get_gate] = broken_dependency
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/agent/chat/",
        json={"session_id": "test-session", "message": "question"},
    )

    assert response.status_code == 500
    assert response.json() == INTERNAL_ERROR
    assert "private dependency path and secret" not in response.text


def test_unhandled_route_exception_returns_private_json_500():
    class BrokenGate:
        def choice(self, **kwargs):
            raise KeyError("private route path and secret")

    app.dependency_overrides[get_gate] = BrokenGate
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/agent/chat/",
        json={"session_id": "test-session", "message": "question"},
    )

    assert response.status_code == 500
    assert response.json() == INTERNAL_ERROR
    assert "private route path and secret" not in response.text


@pytest.mark.parametrize(
    "error",
    [
        APIConnectionError(
            #创建一个HTTP请求对象，并且传入请求方法和请求目标地址
            request=httpx.Request("POST", "https://example.invalid")
        ),
        APITimeoutError(
            request=httpx.Request("POST", "https://example.invalid")
        ),
        APIStatusError(
            "private upstream error",
            response=httpx.Response(
                429,
                request=httpx.Request("POST", "https://example.invalid"),
            ),
            body=None,
        ),
    ],
    ids=["connection", "timeout", "status"],
)
def test_recognized_route_service_exception_remains_json_503(error: Exception):
    class UnavailableGate:
        def choice(self, **kwargs):
            raise error

    app.dependency_overrides[get_gate] = UnavailableGate
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/agent/chat/",
        json={"session_id": "test-session", "message": "question"},
    )

    assert response.status_code == 503
    assert response.json() == SERVICE_UNAVAILABLE
    assert "private upstream error" not in response.text


def test_recognized_dependency_service_exception_remains_json_503():
    def unavailable_dependency():
        raise APIConnectionError(
            request=httpx.Request("POST", "https://example.invalid")
        )

    app.dependency_overrides[get_gate] = unavailable_dependency
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/agent/chat/",
        json={"session_id": "test-session", "message": "question"},
    )

    assert response.status_code == 503
    assert response.json() == SERVICE_UNAVAILABLE


def test_request_validation_remains_json_422_without_executing_route():
    calls = []

    class RecordingGate:
        def choice(self, **kwargs):
            calls.append("called")
            return "answer"

    def recording_dependency():
        return RecordingGate()

    app.dependency_overrides[get_gate] = recording_dependency
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/agent/chat/",
        json={"session_id": "test-session", "message": "   "},
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "invalid_request",
        "message": "Invalid request",
    }
    assert calls == []


def test_normal_chat_response_remains_unchanged():
    class AnsweringGate:
        def choice(self, *, session_id: str, user_input: str) -> str:
            assert session_id == "test-session"
            assert user_input == "question"
            return "answer"

    app.dependency_overrides[get_gate] = AnsweringGate
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/agent/chat/",
        json={"session_id": "test-session", "message": "question"},
    )

    assert response.status_code == 200
    assert response.json() == {"answer": "answer"}
