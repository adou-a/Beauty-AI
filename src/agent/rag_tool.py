from src.rag.retriever import Retriever


RAG_KNOWLEDGE_GUIDANCE = (
    "专业事实必须依据当前检索到的 KnowledgeFacts。"
    "可以总结、改写和通俗化，但不能改变原意、提高结论强度。"
    "KnowledgeFacts 没有提供的专业事实不要自行补充。"
    "这些 KnowledgeFacts 是证据池，不是回答清单。"
    "最终回答必须重新围绕用户当前问题本身，只选择完成当前问题所必要的 facts。"
    "不要因为某个 fact 被检索出来，就自动把它加入最终答案。"
    "如果当前问题是简单单一意图，只回答该意图对应的内容；"
    "其他 category 即使已经检索到，也必须省略。"
    "不要在回答完成后主动追加用户没有询问的风险、使用方法、浓度、搭配、"
    "适用人群或其他专业维度。"
    "回答完成当前问题后直接结束，不要继续扩展成成分百科。"
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
