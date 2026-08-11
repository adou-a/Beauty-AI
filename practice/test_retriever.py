from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever


embedding_service = EmbeddingService()

vector_store = VectorStore()
vector_store.load()

retriever = Retriever(embedding_service = embedding_service,vector_store = vector_store,top_k = 3)
query = ('护肤以后总是刺痛是什么原因？')
results = retriever.retriever(query)

print('Query: ',query)
print('=' * 60)

for rank,result in enumerate(results,start=1):

    print('Rank: ',rank)
    print('Score: ',result.score)
    print('source: ',result.chunk.source)
    print('index: ',result.chunk.index)
    print('content: ',result.chunk.content)
    print('-' * 60)