from src.rag.retriever import Retriever
from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
embedding_service = EmbeddingService()
vector_store = VectorStore()
vector_store.load()
retriever = Retriever(embedding_service = embedding_service,vector_store = vector_store,top_k =  3)

results = retriever.retriever("视黄醇的作用")
for result in results:
    print("ID:", result.id)
    print("Ingredient:", result.ingredient)
    print("Category:", result.category)
    print("Content:", result.content)
    print("Source:", result.source)