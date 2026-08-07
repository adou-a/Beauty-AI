from src.agent.agent import BeautyAgent
from src.agent.session_memory import MemoryStore



class FakeLLM:

    def __init__(self):
        self.messsages_history = []


    def chat(self,messages,tools):

        self.messages_history = messages

        class Response:
            tool_calls = None
            content = '这是回答'


        return Response()


class FakeExecutor:

    def execute(self,tool_call):
        return {}

def test_agent_memory():

    memory_store = MemoryStore()
    llm = FakeLLM()
    agent = BeautyAgent(tools=[],llm=llm,executor=FakeExecutor(),memory_store=memory_store)



    result1 = agent.run('user001','烟酰胺是什么')
    print(result1)


    result2 = agent.run('user001','它适合油皮吗')


    print(result2)


    memory = memory_store.get_memory('user001')


    messages = memory.get_messages()
    print(messages)
    print(llm.messages_history)


result = test_agent_memory()
print(result)