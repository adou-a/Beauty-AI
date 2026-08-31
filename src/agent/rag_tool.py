from src.rag.retriever import Retriever


RAG_KNOWLEDGE_GUIDANCE = (
    "回答专业事实时应依据当前检索到的知识事实。"
    "可以总结和改写，但不要扩大原始结论。"
    "知识事实未提供的信息不要自行补充。"
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
