from src.rag.loader import DocumentLoader
from src.rag.chunker import TextChunker
from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
from src.rag.indexer import KnowledgeIndexer


loader = DocumentLoader()

chunker = TextChunker(chunk_size=500, overlap=100)
embedding_service = EmbeddingService()
vector_store = VectorStore()
indexer = KnowledgeIndexer(loader=loader,chunker=chunker,embedding_service=embedding_service,vector_store=vector_store)

count = indexer.bulid('data/knowledge')

print('Index chunks: ',count)
print('Vector store count: ',vector_store.count())