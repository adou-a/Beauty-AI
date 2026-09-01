import json
from pathlib import Path

from src.rag.models import EmbeddedKnowledgeFact, KnowledgeFact, Source
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.agent.rag_tool import RAGTool

def test_vector_store_returns_most_similar_fact():

    store = VectorStore()

    store.add_many(
        [
            EmbeddedKnowledgeFact(
                fact=KnowledgeFact(
                    id="sensitive-001",
                    ingredient="敏感肌",
                    category="skin_suitability",
                    content="敏感肌知识",
                    source=[Source(name="sensitive.md")]
                ),
                vector=[1.0, 0.0]
            ),
            EmbeddedKnowledgeFact(
                fact=KnowledgeFact(
                    id="sunscreen-001",
                    ingredient="防晒剂",
                    category="effect",
                    content="防晒知识",
                    source=[Source(name="sunscreen.md")]
                ),
                vector=[0.0, 1.0]
            )
        ]
    )

    results = store.search(
        query_vector=[0.9, 0.1],
        top_k=1
    )

    assert len(results) == 1

    assert results[0].fact.id == "sensitive-001"
    assert results[0].fact.source == [Source(name="sensitive.md")]
    assert isinstance(results[0].score, (int, float))

class FakeEmbeddingService:

    def embed_text(
        self,
        text: str
    ) -> list[float]:

        if "敏感" in text:
            return [1.0, 0.0]

        return [0.0, 1.0]

def test_retriever_returns_relevant_knowledge():

    embedding = FakeEmbeddingService()

    store = VectorStore()

    store.add_many(
        [
            EmbeddedKnowledgeFact(
                fact=KnowledgeFact(
                    id="sensitive-risk-001",
                    ingredient="敏感肌",
                    category="risk",
                    content="敏感肌容易出现刺激反应",
                    source=[Source(name="sensitive.md")]
                ),
                vector=[1.0, 0.0]
            ),
            EmbeddedKnowledgeFact(
                fact=KnowledgeFact(
                    id="sunscreen-effect-001",
                    ingredient="防晒剂",
                    category="effect",
                    content="防晒有助于减少紫外线损伤",
                    source=[Source(name="sunscreen.md")]
                ),
                vector=[0.0, 1.0]
            )
        ]
    )

    retriever = Retriever(
        embedding_service=embedding,
        vector_store=store,
        top_k=1
    )

    results = retriever.retriever(
        "敏感肌需要注意什么？"
    )

    assert isinstance(results[0], KnowledgeFact)
    assert results[0].id == "sensitive-risk-001"
    assert results[0].source == [Source(name="sensitive.md")]
    assert results[0].category == "risk"

class FakeRetriever:

    def __init__(self):
        self.queries = []

    def retriever(self,query):
        self.queries.append(query)

        return [
            KnowledgeFact(
                id="retinol-risk-001",
                ingredient="视黄醇",
                category="risk",
                content=(
                    "视黄醇初次使用时"
                    "可能出现干燥和蜕皮"
                ),
                source=[
                    Source(
                        name="AAD article",
                        type="AAD",
                        url="https://example.com"
                    ),
                    Source(name="Source without metadata")
                ]
            ),
            KnowledgeFact(
                id="retinol-function-001",
                ingredient="视黄醇",
                category="function",
                content="视黄醇具有护肤作用",
                source=[Source(name="Function source")]
            ),
            KnowledgeFact(
                id="retinol-usage-001",
                ingredient="视黄醇",
                category="usage",
                content="视黄醇应按产品说明使用",
                source=[Source(name="Usage source")]
            )
        ]


def test_rag_tool_returns_structured_facts():

    retriever = FakeRetriever()

    rag_tool = RAGTool(retriever=retriever)


    query = 'A醇为什么会脱皮'
    result = rag_tool.search_knowledge(query)

    assert result['query'] == query
    assert retriever.queries == [query]
    assert isinstance(result['facts'], list)
    assert len(result['facts']) == 3
    assert [fact['id'] for fact in result['facts']] == [
        'retinol-risk-001',
        'retinol-function-001',
        'retinol-usage-001'
    ]

    fact = result['facts'][0]
    assert set(fact) == {
        'id',
        'ingredient',
        'category',
        'content',
        'source'
    }
    assert fact['id'] == 'retinol-risk-001'
    assert fact['ingredient'] == '视黄醇'
    assert fact['category'] == 'risk'
    assert '视黄醇' in fact['content']
    assert isinstance(fact['source'], list)
    assert fact['source'] == [
        {
            'name': 'AAD article',
            'type': 'AAD',
            'url': 'https://example.com'
        },
        {
            'name': 'Source without metadata',
            'type': None,
            'url': None
        }
    ]

    assert isinstance(result['guidance'], str)
    assert result['guidance'].strip()
    assert '专业事实必须依据当前检索到的 KnowledgeFacts' in result['guidance']
    assert '不能改变原意、提高结论强度' in result['guidance']
    assert 'KnowledgeFacts 没有提供的专业事实不要自行补充' in result['guidance']
    assert '证据池，不是回答清单' in result['guidance']
    assert '最终回答必须重新围绕用户当前问题本身' in result['guidance']
    assert '其他 category 即使已经检索到，也必须省略' in result['guidance']
    assert '回答完成当前问题后直接结束' in result['guidance']

    assert 'context' not in result
    assert 'sources' not in result
    assert 'score' not in fact
    assert 'vector' not in fact

    json.dumps(result, ensure_ascii=False)


def test_vector_store_source_round_trip(tmp_path: Path):
    storage_path = tmp_path / 'vector_store.json'
    fact = KnowledgeFact(
        id='retinol-risk-001',
        ingredient='retinol',
        category='risk',
        content='Retinol may cause dryness.',
        source=[
            Source(
                name='Source A',
                type='official',
                url='https://example.com'
            ),
            Source(name='Source B')
        ]
    )
    store = VectorStore(storage_path=str(storage_path))
    store.add(EmbeddedKnowledgeFact(fact=fact, vector=[1.0, 0.0]))

    store.save()

    raw_data = json.loads(storage_path.read_text(encoding='utf-8'))
    assert raw_data[0]['fact']['source'] == [
        {
            'name': 'Source A',
            'type': 'official',
            'url': 'https://example.com'
        },
        {
            'name': 'Source B',
            'type': None,
            'url': None
        }
    ]

    loaded_items = VectorStore(storage_path=str(storage_path)).load()
    loaded_sources = loaded_items[0].fact.source

    assert all(isinstance(source, Source) for source in loaded_sources)
    assert loaded_sources == fact.source
