from src.rag.models import EmbeddedKnowledgeFact, KnowledgeFact
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
                    source=["sensitive.md"]
                ),
                vector=[1.0, 0.0]
            ),
            EmbeddedKnowledgeFact(
                fact=KnowledgeFact(
                    id="sunscreen-001",
                    ingredient="防晒剂",
                    category="effect",
                    content="防晒知识",
                    source=["sunscreen.md"]
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
    assert results[0].fact.source == ["sensitive.md"]
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
                    source=["sensitive.md"]
                ),
                vector=[1.0, 0.0]
            ),
            EmbeddedKnowledgeFact(
                fact=KnowledgeFact(
                    id="sunscreen-effect-001",
                    ingredient="防晒剂",
                    category="effect",
                    content="防晒有助于减少紫外线损伤",
                    source=["sunscreen.md"]
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
    assert results[0].source == ["sensitive.md"]
    assert results[0].category == "risk"

class FakeRetriever:

    def retriever(self,query):


        return [
            KnowledgeFact(
                id="retinol-risk-001",
                ingredient="视黄醇",
                category="risk",
                content=(
                    "视黄醇初次使用时"
                    "可能出现干燥和蜕皮"
                ),
                source=["retinol.md"]
            )
        ]


def test_rag_tool_returns_structured_facts():

    retriever = FakeRetriever()

    rag_tool = RAGTool(retriever=retriever)


    query = 'A醇为什么会脱皮'
    result = rag_tool.search_knowledge(query)

    assert result['query'] == query
    assert isinstance(result['facts'], list)
    assert len(result['facts']) == 1

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
    assert fact['source'] == ['retinol.md']

    assert isinstance(result['guidance'], str)
    assert result['guidance'].strip()
    assert '资料不足' in result['guidance']
    assert '编造' in result['guidance']

    assert 'context' not in result
    assert 'sources' not in result
