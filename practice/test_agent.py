from src.agent.main import agent

def test_agent():
    result = agent.run('烟酰胺适合油皮吗')
    print(result)



if __name__ =='__main__':
    test_agent()



