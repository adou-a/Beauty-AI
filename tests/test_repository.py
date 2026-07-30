# from pathlib import Path
# import sys

# PATH_DIR = Path(__file__).resolve().parent.parent

# sys.path.append(str(PATH_DIR))
from src.services.ingredient_service  import Service
from src.services.ingredient_repository import IngredientRepository





def test_total_ingredients():
    repository = IngredientRepository()
    service =Service(repository)
    ingredients = service.total_ingredients()
    assert len(ingredients) > 0


