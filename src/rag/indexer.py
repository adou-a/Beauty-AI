from src.rag.embedding import EmbeddingService
from src.rag.models import EmbeddedKnowledgeFact, KnowledgeFact
from src.rag.vector_store import VectorStore
from src.utils.logger import get_logger

logger = get_logger(__name__)

class KnowledgeIndexer:

    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):

        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def build(self, facts: list[KnowledgeFact]) -> int:
        if not facts:
            raise ValueError('Knowledge facts cannot be empty')

        logger.info('Knowledge indexing started')
        embedded_facts: list[EmbeddedKnowledgeFact] = []

        for fact in facts:
            embedded_facts.append(self.embedding_service.embed_fact(fact))

        logger.info('Knowledge facts embedded: %s', len(embedded_facts))

        self.vector_store.clear()
        self.vector_store.add_many(embedded_facts)
        self.vector_store.save()
        count = self.vector_store.count()
        logger.info('Knowledge indexing completed: %s', count)
        return count
