class BeautyAgent:

    def __init__(self,tools):
        self.tools = tools


    def run(self,user_input:str):
        print('Thinking...')
        if '成分' in user_input:
            result = (self.tools['search_ingredient']('烟酰胺'))
            print('Observation: ',result)
            return result


        return '无法处理'