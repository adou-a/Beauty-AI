from src.rag.retriever import Retriever


RAG_KNOWLEDGE_GUIDANCE = (
    '优先依据检索到的知识事实回答。'
    '如果当前知识事实不足以支持结论，应明确说明资料不足。'
    '不要根据缺失信息编造事实。'
)


class RAGTool:
    def __init__(self,retriever: Retriever):

        self.retriever = retriever

    def search_knowledge(self,query: str) -> dict:

        facts = self.retriever.retriever(query)

        return {
            'query': query,
            'facts': [
                {
                    'id': fact.id,
                    'ingredient': fact.ingredient,
                    'category': fact.category,
                    'content': fact.content,
                    'source': [
                        {
                            'name': source.name,
                            'type': source.type,
                            'url': source.url
                        }
                        for source in fact.source
                    ]
                }
                for fact in facts
            ],
            'guidance': RAG_KNOWLEDGE_GUIDANCE
        }
