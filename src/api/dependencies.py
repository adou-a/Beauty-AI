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


