from src.agent.agent import BeautyAgent
from src.agent.memory import ConversationMemory
from src.api import dependencies
from src.exceptions.agent_exception import ToolExecutionError, ToolNotFoundError
from src.agent.executor import ToolExecutor
from src.rag.models import KnowledgeFact, Source
import pytest
import json
from src.agent.session_memory import MemoryStore


def test_answer_focus_contract_is_strict():
    system_prompt = ConversationMemory().get_messages()[0]["content"]

    assert "Retrieved KnowledgeFacts 是证据池，不是回答清单" in system_prompt
    assert "某个 fact 被检索出来，不代表必须写入答案" in system_prompt
    assert "“是什么”只回答 definition" in system_prompt
    assert "“有什么作用”只回答 function" in system_prompt
    assert "“有什么风险”只回答 risk" in system_prompt
    assert "“怎么使用”只回答 usage" in system_prompt
    assert "简单单一意图问题禁止写成成分百科" in system_prompt

class FakeToolCall:

    def __init__(self,name,arguments='{}',call_id = 'call_001'):

        self.id = call_id
        self.function = Fakefunction(name=name,arguments=arguments)



class FakeResponse:

    def __init__(self,tool_calls = None,content = None):

        self.tool_calls = tool_calls
        self.content = content

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


class ContractEmbeddingService:
    pass


class ContractVectorStore:
    def load(self):
        return []


class ContractRetriever:
    def __init__(self, embedding_service, vector_store, top_k):
        self.top_k = top_k

    def retriever(self, query):
        return [
            KnowledgeFact(
                id="retinol_definition_001",
                ingredient="视黄醇（Retinol）",
                category="definition",
                content="视黄醇是维生素A的一种形式。",
                source=[
                    Source(
                        name="grounded-source",
                        type="reference",
                        url="https://example.com/retinol",
                    )
                ],
            )
        ]


def test_production_agent_uses_only_search_knowledge(monkeypatch):
    monkeypatch.setattr(
        dependencies,
        "EmbeddingService",
        ContractEmbeddingService,
    )
    monkeypatch.setattr(
        dependencies,
        "VectorStore",
        ContractVectorStore,
    )
    monkeypatch.setattr(
        dependencies,
        "Retriever",
        ContractRetriever,
    )
    monkeypatch.setattr(
        dependencies,
        "get_llm_client",
        lambda: object(),
    )

    agent = dependencies.get_agent()
    tool_names = [tool["function"]["name"] for tool in agent.tools]
    registry = agent.executor.registry

    assert tool_names == ["search_knowledge"]
    assert not registry.exists("search_ingredient")
    assert not registry.exists("check_skin_risk")
    assert registry.exists("search_knowledge")

    result = agent.executor.execute(
        FakeToolCall(
            name="search_knowledge",
            arguments='{"query": "视黄醇是什么"}',
        )
    )

    assert result["query"] == "视黄醇是什么"
    assert result["facts"][0]["id"] == "retinol_definition_001"
    assert result["facts"][0]["source"] == [
        {
            "name": "grounded-source",
            "type": "reference",
            "url": "https://example.com/retinol",
        }
    ]

    monkeypatch.setattr(dependencies, "get_agent", lambda: agent)
    gate = dependencies.get_gate()

    assert gate.agent is agent
    assert gate.workflow_runner.plan_executor.step_executor.agent is agent
