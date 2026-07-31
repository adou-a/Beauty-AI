from src.ai.llm_client import LLMClient


client = LLMClient()

result = client.chat('烟酰胺有什么作用')

print(result)