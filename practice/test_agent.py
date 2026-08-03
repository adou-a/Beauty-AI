from src.agent.agent import BeautyAgent
from src.agent.tools  import search_ingredient




tools = {
    'search_ingredient':search_ingredient

}

agent = BeautyAgent(tools)


result = agent.run('查询烟酰胺这个成分')

print(result)