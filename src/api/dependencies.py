from src.agent.schemas import (ingredient_tool_schema,search_ingredient_schema)
from src.services.ingredient_repository import IngredientRepository
from src.services.ingredient_service import IngredientService
from src.agent.tools import IngredientSearchTool
from src.agent.registry import ToolRegistry
from src.agent.executor import ToolExecutor
from src.agent.agent import BeautyAgent
from src.ai.ai_service import AIService
from src.ai.llm_client import LLMClient
from src.agent.session_memory import MemoryStore

def get_ingredient_service():
    respository = IngredientRepository()
    return IngredientService(respository)



def get_llm_client():
    return LLMClient()

def get_ai_service():
    ingredient_service = get_ingredient_service()
    llm = LLMClient()
    return AIService(ingredient_service,llm)

memory_store = MemoryStore()
def get_agent():

    ingredient_service  = get_ingredient_service()
    tool = IngredientSearchTool(ingredient_service)
    registry = ToolRegistry()

    registry.register('search_ingredient',tool.search_ingredient)
    registry.register('check_skin_risk',tool.check_skin_risk)
    executor = ToolExecutor(registry)

    llm = get_llm_client()

    tools = [ingredient_tool_schema,
            search_ingredient_schema]

   

    agent = BeautyAgent(tools=tools,llm=llm,executor=executor,memory_store=memory_store)
    return agent