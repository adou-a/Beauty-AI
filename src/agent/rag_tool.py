from src.rag.retriever import Retriever
from src.rag.rag_service import build_context


class RAGTool:
    def __init__(self,retriever: Retriever):

        self.retriever = retriever

    def search_knowledge(self,query: str) -> dict:

        results = self.retriever.retriever(query)

        context = build_context(results)

        sources = []

        for result in results:
            sources.append(
                {
                    'source': result.chunk.source,
                    'index': result.chunk.index
                }
            )

        return{
            'query': query,
            'context': context,
            'sources': sources
        }