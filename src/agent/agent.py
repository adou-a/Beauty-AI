from src.ai.llm_client import LLMClient
import json




class BeautyAgent:

    def __init__(self,tools,llm:LLMClient,executor):
        self.tools = tools
        self.llm  = llm
        
        self.executor = executor


    def run(self,user_input:str):
        messages = [
            {
                'role': 'system',
                'content':
                '''
                你是一个专业护肤分析助手
                你可以调用工具解决问题
                '''
            },
            {
                'role': 'user',
                'content': user_input
            }
        ]

        while True:
            response = self.llm.chat(messages,self.tools)

            if response.tool_calls:
                tool_call = response.tool_calls[0]
                messages.append(
                    {
                        'role': 'assistant',
                        'tool_calls': [
                            {
                                'id': tool_call.id,
                                'type': 'function',
                                'function':{
                                    'name': tool_call.function.name,
                                    'arguments': tool_call.function.arguments
                                }
                            }
                        ]
                    }
                )
                result = self.executor.execute(tool_call)

                messages.append(
                    {
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': json.dumps(serialize_result(result),ensure_ascii= False)
                    }
                )
                
                continue

                

            else:

                return response.content    

     



def serialize_result(result):

    if hasattr(result,"__dict__"):
        return result.__dict__

    if isinstance(result,dict):
        return result

    return str(result)
        