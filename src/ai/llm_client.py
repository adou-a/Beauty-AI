from src.config.settings import DEEPSEEK_API_KEY
from openai import OpenAI
from openai import OpenAIError


class LLMClient:

    def __init__(self) -> None:
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY,base_url='https://api.deepseek.com')



    def chat(self,message:str) -> str:
        try:
            response = self.client.chat.completions.create(
                model = 'deepseek-chat',messages = [

                    {
                        "role":"system",
                        "content":
                        "你是一名专业护肤分析助手"
                    },

                    {
                        "role":"user",
                        "content":message
                    }

                ]

            )
            print(response)
            return response.choices[0].message.content

        except OpenAIError as e:
            print(e)
            raise
        
            
        