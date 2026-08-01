from src.services.ingredient_repository import IngredientRepository
from src.services.ingredient_service import IngredientService
from src.ai.ai_service import AIService
from src.ai.llm_client import LLMClient

def get_ingredient_service():
    respository = IngredientRepository()
    return IngredientService(respository)

def get_ai_service():
    ingredient_service = get_ingredient_service()
    llm_client = LLMClient()
    return AIService(ingredient_service,llm_client)