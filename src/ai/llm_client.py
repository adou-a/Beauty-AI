from src.config.settings import (DEEPSEEK_API_KEY,DEEPSEEK_MODEL)
from src.exceptions.llm_exception import (LLMConnectionError,LLMResponseError)
from openai import OpenAI
import logging




logger = logging.getLogger(__name__)
class LLMClient:

    def __init__(self) -> None:
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY,base_url='https://api.deepseek.com')



    def chat(self, messages: list[dict[str, str]] | str, tools=None):
        if isinstance(messages, str):
            messages = [
                {
                    'role': 'user',
                    'content': messages,
                }
            ]

        logger.info('sending request to LLM')
        response = self.client.chat.completions.create(
            model = DEEPSEEK_MODEL,
            messages = messages,
            tools= tools
            )
        return response.choices[0].message
