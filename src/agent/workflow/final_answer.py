FINAL_ANSWER_PROMPT = f'''

'''

class FinalAnswer:

    def __init__(self,llm):
        self.llm = llm

    def synthesis(self,results,user_input):
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
        return result

    def _bulit_prompt(self,results):
        return f'''
  
请根据以下结果，回答用户的问题
{results}

要求：
1.严格按照结果来回答
2.不能添加额外知识答案
3.结果在300字以内
输出成一段完整的回答


'''
        

        
