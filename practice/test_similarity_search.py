from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore



embedding_service = EmbeddingService()

vector_store = VectorStore()
vector_store.load()


query = ('最近换护肤品以后脸特别容易红怎么办？')
query_vector = embedding_service.embed_text(query)


results = vector_store.search(query_vector=query_vector,top_k=3)

print('Query: ',query)
print('=' *60)

for position, result in enumerate(results,start=1):
    print('Rank: ',position)
    print('Score:', result.score)

    print('source: ',result.chunk.source)

    print('index: ',result.chunk.index)
    print('content: ',result.chunk.content)
    print('-' * 60)