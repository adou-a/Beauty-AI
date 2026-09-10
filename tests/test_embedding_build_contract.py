import pytest

from src.rag import embedding as embedding_module


EXPECTED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EXPECTED_REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"


def test_embedding_service_uses_fixed_model_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    constructor_call: dict[str, object] = {}

    class FakeSentenceTransformer:
        def __init__(self, model_name: str, **kwargs: object) -> None:
            constructor_call["model_name"] = model_name
            constructor_call.update(kwargs)

    monkeypatch.setattr(
        embedding_module,
        "SentenceTransformer",
        FakeSentenceTransformer,
    )

    service = embedding_module.EmbeddingService()

    assert service.model_name == EXPECTED_MODEL
    assert service.revision == EXPECTED_REVISION
    assert constructor_call == {
        "model_name": EXPECTED_MODEL,
        "revision": EXPECTED_REVISION,
    }
