from src.services.ingredient_service  import IngredientService
from src.services.ingredient_repository import IngredientRepository





def test_total_ingredients():
    repository = IngredientRepository()
    service =IngredientService(repository)
    ingredients = service.total_ingredients()
    assert len(ingredients) > 0


