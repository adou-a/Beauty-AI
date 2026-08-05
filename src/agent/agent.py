from src.ai.llm_client import LLMClient





class BeautyAgent:

    def __init__(self,tools,llm:LLMClient,executor):
        self.tools = tools
        self.llm  = llm
        
        self.executor = executor


    def run(self,user_input:str):

        while True:
            response = self.llm.chat(user_input,self.tools)

            if response.tool_calls:
                result = self.executor.execute(response.tool_calls[0])
                
                final_response = (self.llm.chat(f'''
            用户问题：
            {user_input}
            工具返回：
            {result}
            请回答用户
            ''')
                                )

                return final_response.content

        else:

            return response.content    

     

        