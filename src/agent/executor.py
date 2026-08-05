import json

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


        #执行函数
        result = tool(**arguments)

        return result