from src.ai.llm_client import LLMClient



class AIService:
    def __init__(self):
        self.client = LLMClient()


    def analyze(self,question:str):
        response = self.client.chat(question)
        return response




    