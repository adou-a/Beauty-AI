

class FinalAnswer:

    def __init__(self,llm):
        self.llm = llm

    def synthesis(self,results,user_input) -> str:
        message = self._bulit_prompt(results)

        messages=[
            {
                'role': 'system',
            'content':message
            },
            {
                'role':'user',
                'content':user_input
            }
        ]
        result = self.llm.chat(messages)
        if isinstance(result, str):
            return result
        return result.content

    def _bulit_prompt(self,results):
        return f'''
你是 Beauty-AI，一个专注于化妆品和护肤领域的 AI 助手
请根据以下结果，回答用户的问题
{results}

回答规则：

1. 只能使用提供的执行结果回答，不要补充执行结果之外的信息。
2. 不要编造不存在的事实。
3. 将多个执行步骤的结果整合成一个完整、自然的用户答案。
4. 不要展示系统内部过程，包括：
   - Step
   - Planner
   - Agent
   - Tool
   - RAG
   - 执行结果
   - 推理过程

5. 输出应该像专业护肤顾问给用户的回答，而不是技术报告。

格式要求：

- 使用自然语言段落。
- 如果信息较多，可以使用简单列表。
- 保持结构清晰。

禁止使用：

- Markdown标题符号(#)
- 加粗符号（**)
- 代码格式
- 内部技术术语

长度要求：

- 普通问题控制在300字以内。
- 保证回答完整，不要为了缩短而遗漏关键内容。
'''
        

        
