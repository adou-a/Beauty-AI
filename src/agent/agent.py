from src.exceptions.agent_exception import ToolExecutionError, ToolNotFoundError
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
        #说明提供给llm的工具
        allowed_tool_names = {
            tool['function']['name']
            for tool in self.tools
        }
        #布尔状态变量
        invalid_tool_retry_used = False
        while True:
            logger.info('Calling LLM')
            #找一个retry信息，和用户信息区分开
            retry_messages = messages
            while True:
                #第一次提供原信息，如果第一次有错给的是错误信息
                response = self.llm.chat(retry_messages,self.tools)
                #如果不需要工具直接回答就跳出
                if not response.tool_calls:
                    break
                #找到response.tool_calls中不正确的工具
                invalid_tool_names = sorted({
                    tool_call.function.name
                    for tool_call in response.tool_calls
                    if tool_call.function.name not in allowed_tool_names
                })
                #如果没有异常工具就跳出
                if not invalid_tool_names:
                    break
                
                allowed_names = sorted(allowed_tool_names)
                logger.warning(
                    'Invalid tool selected: %s',
                    ', '.join(invalid_tool_names),
                )
                logger.warning(
                    'Allowed tools: %s',
                    ', '.join(allowed_names),
                )
                #如果第二次还是有异常工具出现就抛出异常
                if invalid_tool_retry_used:
                    logger.error(
                        'Invalid tool selected again after retry: %s',
                        ', '.join(invalid_tool_names),
                    )
                    raise ToolNotFoundError(
                        'Invalid tool selected after retry: '
                        + ', '.join(invalid_tool_names)
                    )
                #第一次出错把布尔状态改成true
                invalid_tool_retry_used = True
                logger.warning('Retrying invalid tool call once')
                correction_message = {
                    'role': 'system',
                    'content': (
                        '刚才生成了不存在的工具名：\n'
                        f'{", ".join(invalid_tool_names)}\n\n'
                        '当前允许使用的工具只有：\n'
                        f'{", ".join(allowed_names)}\n\n'
                        '请重新生成tool calls，只能使用已经提供的合法工具名，'
                        '不得创建、修改或猜测其他工具名。'
                    ),
                }
                #把错误信息也加入messages组成新信息给llm
                retry_messages = [*messages, correction_message]

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
                        raise
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
        
