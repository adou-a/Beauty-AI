from src.rag.models import SearchResult
from src.rag.retriever import Retriever


def build_context(results: list[SearchResult]) -> str:

    context_parts = []

    for index, result in enumerate(results,start = 1):
        context_parts.append(
            f'''
[资料{index}]
来源：{result.chunk.source}

{result.chunk.content}
'''.strip()
        )
    #换行两次更好区分，把列表合并成字符串
    return '\n\n'.join(context_parts)


class RAGService:
    def __init__(self,retriever: Retriever,llm):
        self.retriever = retriever
        self.llm  = llm

    def ask(self,query: str) -> str:

        results = self.retriever.retriever(query)
        context = build_context(results)

        messages = [
            {
                'role': 'system',
                'content':(
                    '你是一个护肤知识助手'
                    '请优先根据提供的参考资料回答'
                    '如果参考资料不足以支持结论'
                    '请明确说明资料不足'
                    '不要编造知识'
                )
            },
            {
                'role': 'user',
                'content':(
                    f'参考资料: \n\n'
                    f'{context}\n\n'
                    f'用户问题: \n'
                    f'{query}'
                )
            }
        ]

        response = self.llm.chat(messages = messages)
        return response