from src.api.dependencies import get_agent

def test_agent():
    agent = get_agent()
    result = agent.run('我是油敏肌，晚上想用烟酰胺，帮我分析一下')
    print(result)



if __name__ =='__main__':
    test_agent()



