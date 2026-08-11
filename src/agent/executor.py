from src.exceptions.agent_exception import (ToolNotFoundError,ToolExecutionError)
from src.utils.logger import get_logger
import json


logger = get_logger(__name__)
class ToolExecutor:

    def __init__(self,registry):
        self.registry = registry



    def execute(self,tool_call):
        

        
        #获取工具名字

        tool_name = (tool_call.function.name)
        logger.info('Received tool call: %s',tool_name)
       
        #获取参数
        try:
            arguments = json.loads(tool_call.function.arguments)
            logger.info('Tool arguments parsed: %s',arguments)
        except Exception:
            logger.exception('Failed to parse tool arguments')
            raise ToolExecutionError('Invalid arguments')

        #根据名字找到工具

        tool = (self.registry.get(tool_name))
        

        if tool is None:
            logger.exception("Tool not found")
            raise ToolNotFoundError('tool not found')

        logger.info('Executor found tool: %s',tool_name)
        logger.info('Executing tool: %s',tool_name)

        #执行函数
        try:
            result = tool(**arguments)
            logger.info('Tool finished successfully: %s',tool_name)
            return result
        except Exception :
            logger.exception('Tool execution failed: %s',tool_name)
            raise ToolExecutionError('tool execution failed')
    