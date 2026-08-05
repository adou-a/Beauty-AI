from src.config.settings import (DEEPSEEK_API_KEY,DEEPSEEK_MODEL)
from src.exceptions.llm_exception import (LLMConnectionError,LLMResponseError)
from openai import OpenAI
import logging




logger = logging.getLogger(__name__)
class LLMClient:

    def __init__(self) -> None:
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY,base_url='https://api.deepseek.com')



    def chat(self,message:str,tools = None) -> str:
        # try:
            logger.info('sending request to LLM')
            response = self.client.chat.completions.create(
                model = DEEPSEEK_MODEL,messages = [

                    {
                        "role":"system",
                        "content":
                        '''
                        你是一名专业护肤分析助手
                        回答要求：
                        -客观分析护肤成分
                        -不夸大功效
                        -使用普通用户能理解的语言
                        -不代替医生诊
                        '''
                    },
                    {
                        "role":"user",
                        "content":message
                    }

                ],tools= tools

            )
            return response.choices[0].message
        #     if not content:
        #         logger.error('LLM request failed')
        #         raise LLMResponseError('LLM returned empty response')


        #     logger.info('LLM response received')
        #     return content

        # except Exception as e:
        #     logger.error(f'LLM request failed: {e}')

        #     raise LLMConnectionError('LLM service unavailable')
        
            
        