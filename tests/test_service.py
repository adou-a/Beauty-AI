from src.services.ingredient_service import IngredientService
from src.services.ingredient_repository import IngredientRepository
from src.models.ingredient import Ingredient


def test_find_ingredient():

    repository = IngredientRepository()
    service = IngredientService(repository)

    ingredient = service.find_ingredient("烟酰胺")

    assert ingredient is not None
    assert ingredient.chinese_name == "烟酰胺"



def test_find_by_category():

    repository = IngredientRepository()
    service = IngredientService(repository)

    result = service.find_by_category("抗氧化")

    assert len(result) > 0
    assert "绿茶提取物" in [
        ingredient.chinese_name
        for ingredient in result
    ]



def test_find_by_skin_type():

    repository = IngredientRepository()
    service = IngredientService(repository)

    result = service.find_by_skin_type("敏感肌")

    assert len(result) > 0


def test_return_type():

    repository = IngredientRepository()
    service = IngredientService(repository)

    result = service.find_ingredient("烟酰胺")

    assert isinstance(result, Ingredient)