from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.rag.rag_service import RAGService
from src.ai.llm_client import LLMClient



embedding_service = EmbeddingService()
vectore_store = VectorStore()
vectore_store.load()

retriever = Retriever( embedding_service = embedding_service,vector_store = vectore_store,top_k = 3)
llm = LLMClient()

rag_service = RAGService(retriever = retriever,llm = llm )

question = ('Beauty-AI测试知识中的B2代表什么？')

answer  = rag_service.ask(question)
print('Question: ')
print(question)

print('=' * 60)

print('Answer: ')
print(answer)

