from src.ai.ai_service import AIService
from src.ai.llm_client import LLMClient
from src.services.ingredient_service import IngredientService
from src.services.ingredient_repository import IngredientRepository

repositroy = IngredientRepository()

ingredient_service = IngredientService(repositroy)
llm_client = LLMClient()

service = AIService(ingredient_service,llm_client)

result =  service.analyze_ingrdient('烟酰胺')
print(result)
print(result.benefits)