from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
from src.rag.models import KnowledgeFact
from src.utils.logger import get_logger
from src.exceptions.rag_exception import RetrieverError
logger = get_logger(__name__)

class Retriever:

    def __init__(self,embedding_service: EmbeddingService,vector_store: VectorStore,top_k: int = 3):

        if top_k <= 0:
            raise ValueError('top_k must be greater than 0')

        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.top_k = top_k



    def retriever(self,query: str ) -> list[KnowledgeFact]:
        if not query.strip():
            raise ValueError('Query cannot be empty')
        logger.info('Retriever knowledge for query: %s',query)
        try:
            query_vector = self.embedding_service.embed_text(query)

            search_results = self.vector_store.search(query_vector = query_vector,top_k = self.top_k)
            facts = [result.fact for result in search_results]
            logger.info('Retrieved %s knowledge facts',len(facts))

            return facts

        except Exception as exc:
            raise RetrieverError('Knowledge retrieve failed') from exc
