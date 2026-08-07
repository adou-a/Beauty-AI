from src.exceptions.agent_exception import ToolExecutionError
from src.ai.llm_client import LLMClient
import json
from src.utils.logger import get_logger



logger = get_logger(__name__)
class BeautyAgent:

    def __init__(self,tools,llm:LLMClient,executor,memory_store):
        self.tools = tools
        self.llm  = llm
        self.executor = executor
        self.memory_store = memory_store

    def run(self,session_id:str,user_input:str):
        logger.info('Agent received user-input: %s',user_input)
        logger.info('Current session id: %s',session_id)
        memory = self.memory_store.get_memory(session_id)
        memory.add_message(
            {
                'role': 'user',
                'content': user_input
            }
        )
        messages = memory.get_messages()
        while True:
            logger.info('Calling LLM')
            response = self.llm.chat(messages,self.tools)

            if response.tool_calls:
                logger.info('Number of tools selected: %d',len(response.tool_calls))
                assistant_tool_calls = []

                for tool_call in response.tool_calls:
                    logger.info('Agent selected tool: %s',tool_call.function.name)
                    logger.info('Tool arguments: %s', tool_call.function.arguments)
                    assistant_tool_calls.append(
                    {
                        'id' : tool_call.id,
                        'type': 'function',
                        'function':
                        {
                            'name': tool_call.function.name,
                            'arguments': tool_call.function.arguments
                        }
                    }

                    )


                
                memory.add_message(
                    {
                        'role': 'assistant',
                        'tool_calls': assistant_tool_calls
                    }
                    )
                         
                for tool_call in response.tool_calls:
                    try:
                        result = self.executor.execute(tool_call)
                        logger.info('Tool completed: %s',tool_call.function.name)

                        memory.add_message(
                            {
                                'role': 'tool',
                                'tool_call_id': tool_call.id,
                                'content': json.dumps(serialize_result(result),ensure_ascii= False)
            
                            }
                        )
                    except ToolExecutionError as e:
                        logger.error('Agent tool failed: %s',e)
                        return '工具暂时不可用'
                continue

                

            else:
                logger.info('Final answer generated')
                memory.add_message({
                    'role': 'assistant',
                    'content': response.content
                })
                return response.content    

     



def serialize_result(result):

    if hasattr(result,"__dict__"):
        return result.__dict__

    if isinstance(result,dict):
        return result

    return str(result)
        