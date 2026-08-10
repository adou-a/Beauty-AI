from src.rag.loader import DocumentLoader
from src.rag.chunker import TextChunker
from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore


class KnowledgeIndexer:

    def __init__(self,loader: DocumentLoader, chunker: TextChunker, embedding_service: EmbeddingService, vector_store: VectorStore):

        self.loader = loader
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def bulid(self,directory: str) -> int:
        documents = (self.loader.load_directory(directory))

        self.vector_store.clear()

        for document in documents:
            chunks = self.chunker.split(document)

            for chunk in chunks:
                embedded_chunk =(self.embedding_service.embed_chunk(chunk))
                self.vector_store.add(embedded_chunk)

        self.vector_store.save()
        return self.vector_store.count()