from src.agent.main import agent

def test_agent():
    result = agent.run('油敏肌可以使用A醇吗')
    print(result)



if __name__ =='__main__':
    test_agent()



