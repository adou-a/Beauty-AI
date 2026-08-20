from src.agent.agent import BeautyAgent
from src.exceptions.agent_exception import ToolExecutionError, ToolNotFoundError
from src.agent.executor import ToolExecutor
import pytest
import json
from src.agent.session_memory import MemoryStore

class FakeToolCall:

    def __init__(self,name,arguments='{}',call_id = 'call_001'):

        self.id = call_id
        self.function = Fakefunction(name=name,arguments=arguments)



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
        self.calls=[]



    def execute(self,tool_call):
        name = tool_call.function.name

        arguments = json.loads(tool_call.function.arguments)

        self.calls.append({
            'name': name,
            'arguments': arguments
        })
        if name == 'search_knowledge':
            return{
                'knowledge':
                '皮肤屏障受损以后,皮肤对外界刺激的防御能力下降'
            }

        elif name == 'search_ingredient':
            return{
                'name': '烟酰胺',
                'effect': '护肤成分'
            }

        elif name == 'check_skin_risk':

            return{
                'skin_type': '敏感肌',
                'risk': '需要注意刺激'
            }
        return {}

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


class ToolExecutionFailingRegistry:

    def get(self, name):
        def failing_tool():
            raise RuntimeError('tool execution failed')

        return failing_tool


class Fakefunction:
    def __init__(self,name,arguments= '{}'):

        self.name = name
        self.arguments = arguments
        




# def test_unknown_tool():

#     llm = ErrorToolLLM()
#     registry = FakeRegistry()

#     executor = ToolExecutor(registry)

#     agent = BeautyAgent(tools=[],llm= llm,executor=executor)
#     with pytest.raises(ToolNotFoundError):
#         agent.run('查询天气')


def test_tool_execution_error_is_propagated():

    agent = BeautyAgent(
        tools=[],
        llm=ErrorToolLLM(),
        executor=ToolExecutor(ToolExecutionFailingRegistry()),
        memory_store=MemoryStore(),
    )

    with pytest.raises(ToolExecutionError):
        agent.run(
            session_id='tool-error-session',
            user_input='执行工具',
        )


class NoToolLLM:

    def __init__(self):

        self.call_count = 0
        self.messages_history = []


    def chat(self,messages,tools):

        self.call_count += 1

        self.messages_history.append(
            [m.copy() for m in messages]

        )

        return FakeResponse(
            content='你好，有什么可以帮你的'
        )



def test_no_tool():

    llm = NoToolLLM()
    executor = FakeExecutor()

    memory_store =MemoryStore()
    agent = BeautyAgent(tools=[],llm=llm,executor=executor,memory_store=memory_store)



    result = agent.run(session_id='test_no_tool',user_input='你好')


    assert result == '你好，有什么可以帮你的'
    assert executor.calls == []
    assert llm.call_count == 1



class RAGToolLLM:
    def __init__(self):
        self.step = 0
        self.messages_history = []



    def chat(self,messages,tools):
        self.step += 1
        self.messages_history.append(
            [m.copy() for m in messages]
        )


        if self.step == 1:
            return FakeResponse(
                tool_calls=[
                    FakeToolCall(
                        name='search_knowledge',
                        arguments= '{"query": "皮肤屏障受损容易刺痛的原因"}'

                    )
                ]
            )


        return FakeResponse(
            content='根据知识库资料，皮肤屏障受损后对外界刺激的防御能力下降，因此更容易出现刺痛。'
        )



def test_rag_tool():

    llm = RAGToolLLM()
    executor = FakeExecutor()
    memory_store = MemoryStore()
    agent = BeautyAgent(tools=[],llm=llm,executor=executor,memory_store=memory_store)


    result = agent.run(session_id='test_rag',user_input='为什么皮肤屏障受损容易刺痛')




    assert executor.calls[0]['name'] == \
        'search_knowledge'


    assert executor.calls[0]['arguments'] =={
        'query':
        '皮肤屏障受损容易刺痛的原因'
    }

    assert llm.step == 2

    second_messages = (llm.messages_history[1])


    tool_messages = [
        message
        for message in second_messages
        if message.get('role') == 'tool'
    ]


    assert len(tool_messages) == 1
    assert '皮肤屏障' in \
        tool_messages[0]['content']

    assert '皮肤屏障受损' in result


class BusinessToolLLM:

    def __init__(self):

        self.step = 0


    def chat(self, messages, tools):

        self.step += 1


        if self.step == 1:

            return FakeResponse(
                tool_calls=[
                    FakeToolCall(
                        name="search_ingredient",
                        arguments='{"name": "烟酰胺"}'
                    )
                ]
            )


        return FakeResponse(
            content="烟酰胺基础信息查询完成"
        )

def test_business_tool_still_works():

    llm = BusinessToolLLM()

    executor = FakeExecutor()

    memory_store = MemoryStore()


    agent = BeautyAgent(
        tools=[],
        llm=llm,
        executor=executor,
        memory_store=memory_store
    )


    result = agent.run(
        session_id="test_business",
        user_input="查询烟酰胺的信息"
    )


    assert len(executor.calls) == 1


    assert executor.calls[0]["name"] == \
        "search_ingredient"


    assert executor.calls[0]["arguments"] == {
        "name": "烟酰胺"
    }


    assert all(
        call["name"] != "search_knowledge"
        for call in executor.calls
    )


    assert result == \
        "烟酰胺基础信息查询完成"


class MultiToolRAGLLM:

    def __init__(self):

        self.step = 0
        self.messages_history = []


    def chat(self, messages, tools):

        self.step += 1

        self.messages_history.append(
            [m.copy() for m in messages]
        )


        if self.step == 1:

            return FakeResponse(
                tool_calls=[
                    FakeToolCall(
                        name="search_ingredient",
                        arguments='{"name": "视黄醇"}',
                        call_id="call_001"
                    )
                ]
            )


        elif self.step == 2:

            return FakeResponse(
                tool_calls=[
                    FakeToolCall(
                        name="check_skin_risk",
                        arguments='{"skin_type": "敏感肌"}',
                        call_id="call_002"
                    )
                ]
            )


        elif self.step == 3:

            return FakeResponse(
                tool_calls=[
                    FakeToolCall(
                        name="search_knowledge",
                        arguments='{"query": "敏感肌使用视黄醇后脱皮刺痛的注意事项"}',
                        call_id="call_003"
                    )
                ]
            )


        return FakeResponse(
            content="敏感肌使用视黄醇后出现脱皮刺痛，需要降低使用频率并注意皮肤屏障状态。"
        )


def test_multi_tool_with_rag():

    llm = MultiToolRAGLLM()

    executor = FakeExecutor()

    memory_store = MemoryStore()


    agent = BeautyAgent(
        tools=[],
        llm=llm,
        executor=executor,
        memory_store=memory_store
    )


    result = agent.run(
        session_id="test_multi_rag",
        user_input=
        "我是敏感肌，使用视黄醇以后脱皮刺痛，需要注意什么？"
    )


    assert [
        call["name"]
        for call in executor.calls
    ] == [
        "search_ingredient",
        "check_skin_risk",
        "search_knowledge"
    ]


    assert executor.calls[0]["arguments"] == {
        "name": "视黄醇"
    }


    assert executor.calls[1]["arguments"] == {
        "skin_type": "敏感肌"
    }


    assert executor.calls[2]["arguments"] == {
        "query":
        "敏感肌使用视黄醇后脱皮刺痛的注意事项"
    }


    # 3次Tool + 最后1次Final Answer
    assert llm.step == 4


    assert "脱皮刺痛" in result
