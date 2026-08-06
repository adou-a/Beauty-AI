from src.agent.agent import BeautyAgent
from src.exceptions.agent_exception import ToolNotFoundError
from src.agent.executor import ToolExecutor
import pytest


class FakeToolCall:

    def __init__(self,name):

        self.id = 'call_001'
        self.function = Fakefunction(name=name)



class FakeResponse:

    def __init__(self,tool_calls = None,content = None):

        self.tool_calls = tool_calls
        self.content = content

class FakeLLM:
    def __init__(self):
        self.called = False

    def chat(self,messages,tools):
        if not self.called:
            self.called = True
            return FakeResponse(tool_calls= [FakeToolCall('search_ingredient')])

        else:
            return FakeResponse(content= '分析完成')


class MultiToolLLM:
    def __init__(self):
        self.step = 0



    def chat(self,messages,tools):

        self.step += 1

        if self.step == 1:
            return FakeResponse(tool_calls=[FakeToolCall('search_ingredient')])

        elif self.step == 2:
            return FakeResponse(tool_calls=[FakeToolCall('check_skin_risk')])

        else:
            return FakeResponse(content= '完成分析')
        

class FakeExecutor:


    def __init__(self):
        self.called_tools = []



    def execute(self,tool_call):

        self.called_tools.append(tool_call.function['name'])



        return{'name': '烟酰胺',
               'risk': '低'}

class ErrorToolLLM:
    def __init__(self):
        self.called = False
    def chat(self,messages,tools):
        if not self.called:
            self.called = True
            return FakeResponse(tool_calls=[
                FakeToolCall('unknown_tool')
            ])
        return FakeResponse(content='完成')

class FakeRegistry:
    def  get(self,name):
        return None



class ErrorExecutor:

    def execute(self,tool_call):
        raise Exception('ToolNotFoundError')


class Fakefunction:
    def __init__(self,name,arguments= '{}'):

        self.name = name
        self.arguments = arguments
        


# def test_tool_not_found():
#     llm = FakeLLM()

#     executor = ErrorExecutor()


#     agent = BeautyAgent(tools=[],llm = llm, executor = executor)

#     with pytest.raises(Exception):
#         agent.run('查询天气')



# def test_multiple_tools():


#     llm = MultiToolLLM()
#     executor = FakeExecutor()

#     agent = BeautyAgent(tools= [],llm= llm,executor= executor)

#     agent.run('油敏肌使用A醇')

#     assert executor.called_tools == [
#         'search_ingredient',
#         'check_skin_risk'
#     ]

def test_unknown_tool():

    llm = ErrorToolLLM()
    registry = FakeRegistry()

    executor = ToolExecutor(registry)

    agent = BeautyAgent(tools=[],llm= llm,executor=executor)
    with pytest.raises(ToolNotFoundError):
        agent.run('查询天气')