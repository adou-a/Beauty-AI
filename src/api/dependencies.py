from src.services.ingredient_repository import IngredientRepository
from src.services.ingredient_service import IngredientService

def get_ingredient_service():
    respository = IngredientRepository()
    return IngredientService(respository)

