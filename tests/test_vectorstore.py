from src.rag.models import EmbeddedChunk
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.rag.models import SearchResult
from src.agent.rag_tool import RAGTool

def test_vector_store_returns_most_similar_chunk():

    store = VectorStore()

    store.add_many(
        [
            EmbeddedChunk(
                content="敏感肌知识",
                source="sensitive.md",
                index=0,
                vector=[1.0, 0.0]
            ),
            EmbeddedChunk(
                content="防晒知识",
                source="sunscreen.md",
                index=0,
                vector=[0.0, 1.0]
            )
        ]
    )

    results = store.search(
        query_vector=[0.9, 0.1],
        top_k=1
    )

    assert len(results) == 1

    assert (
        results[0].chunk.source
        == "sensitive.md"
    )

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
            EmbeddedChunk(
                content="敏感肌容易出现刺激反应",
                source="sensitive.md",
                index=0,
                vector=[1.0, 0.0]
            ),
            EmbeddedChunk(
                content="防晒有助于减少紫外线损伤",
                source="sunscreen.md",
                index=0,
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

    assert (
        results[0].chunk.source
        == "sensitive.md"
    )

class FakeRetriever:

    def retriever(self,query):


        return[
            SearchResult(
                chunk=EmbeddedChunk(
                    content=(
                        '视黄醇初次使用时'
                        '可能出现干燥和蜕皮'
                    ),
                    source='retinol.md',
                    index=0,
                    vector=[1.0,0.0]
            
                ),
                score = 0.9
            )
        ]


def test_rag_tool_returns_context():

    retriever = FakeRetriever()

    rag_tool = RAGTool(retriever=retriever)


    result = rag_tool.search_knowledge('A醇为什么会脱皮')

    assert '视黄醇' in result['context']

    assert(result['sources'][0]['source'] == 'retinol.md')