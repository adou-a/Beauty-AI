import pytest

from src.rag.indexer import KnowledgeIndexer
from src.rag.models import EmbeddedKnowledgeFact, KnowledgeFact


def make_fact(fact_id: str) -> KnowledgeFact:
    return KnowledgeFact(
        id=fact_id,
        ingredient='retinol',
        category='risk',
        content=f'Knowledge for {fact_id}',
        source=['source.md']
    )


class FakeEmbeddingService:
    def __init__(self, events: list[str], fail_on_id: str | None = None):
        self.events = events
        self.fail_on_id = fail_on_id

    def embed_fact(self, fact: KnowledgeFact) -> EmbeddedKnowledgeFact:
        self.events.append(f'embed:{fact.id}')
        if fact.id == self.fail_on_id:
            raise RuntimeError(f'Embedding failed for {fact.id}')
        return EmbeddedKnowledgeFact(fact=fact, vector=[1.0, 0.0])


class RecordingVectorStore:
    def __init__(
        self,
        events: list[str],
        items: list[EmbeddedKnowledgeFact] | None = None
    ):
        self.events = events
        self.items = list(items or [])

    def clear(self) -> None:
        self.events.append('clear')
        self.items = []

    def add_many(self, items: list[EmbeddedKnowledgeFact]) -> None:
        self.events.append('add_many')
        self.items.extend(items)

    def save(self) -> None:
        self.events.append('save')

    def count(self) -> int:
        return len(self.items)


def test_build_indexes_all_knowledge_facts():
    events = []
    store = RecordingVectorStore(events)
    facts = [make_fact('fact-1'), make_fact('fact-2')]
    indexer = KnowledgeIndexer(FakeEmbeddingService(events), store)

    count = indexer.build(facts)

    assert count == 2
    assert [item.fact for item in store.items] == facts


def test_build_rejects_empty_facts_without_touching_vector_store():
    events = []
    existing = EmbeddedKnowledgeFact(make_fact('existing'), [0.0, 1.0])
    store = RecordingVectorStore(events, [existing])
    indexer = KnowledgeIndexer(FakeEmbeddingService(events), store)

    with pytest.raises(ValueError, match='cannot be empty'):
        indexer.build([])

    assert store.items == [existing]
    assert events == []


def test_embedding_failure_does_not_touch_existing_vector_store():
    events = []
    existing = EmbeddedKnowledgeFact(make_fact('existing'), [0.0, 1.0])
    store = RecordingVectorStore(events, [existing])
    indexer = KnowledgeIndexer(
        FakeEmbeddingService(events, fail_on_id='fact-2'),
        store
    )

    with pytest.raises(RuntimeError, match='Embedding failed for fact-2'):
        indexer.build([make_fact('fact-1'), make_fact('fact-2')])

    assert store.items == [existing]
    assert events == ['embed:fact-1', 'embed:fact-2']


def test_successful_build_replaces_old_items_after_all_embeddings():
    events = []
    existing = EmbeddedKnowledgeFact(make_fact('existing'), [0.0, 1.0])
    store = RecordingVectorStore(events, [existing])
    facts = [make_fact('fact-1'), make_fact('fact-2')]
    indexer = KnowledgeIndexer(FakeEmbeddingService(events), store)

    indexer.build(facts)

    assert [item.fact for item in store.items] == facts
    assert events == [
        'embed:fact-1',
        'embed:fact-2',
        'clear',
        'add_many',
        'save'
    ]
