import json
from src.exceptions.agent_exception import ToolNotFoundError
class ToolExecutor:

    def __init__(self,registry):
        self.registry = registry



    def execute(self,tool_call):

        #获取工具名字

        tool_name = (tool_call.function.name)

        #获取参数

        arguments = json.loads(tool_call.function.arguments)

        #根据名字找到函数

        tool = (self.registry.get(tool_name))
        if tool is None:
            raise ToolNotFoundError('tool not found')


        print('Tool object: ',tool)
        print('Tool type: ', type(tool))
        #执行函数
        result = tool(**arguments)

        return result