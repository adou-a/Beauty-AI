import json
import pytest
from src.services.ingredient_service  import IngredientService
from src.services.ingredient_repository import IngredientRepository
from src.exceptions.ingredient_exception import IngredientDataError




def test_total_ingredients():
    repository = IngredientRepository()
    service =IngredientService(repository)
    ingredients = service.total_ingredients()
    assert len(ingredients) > 0

def test_json_error(monkeypatch):

    def fake_load(file):

        raise json.JSONDecodeError(
            "error",
            "",
            0
        )


    monkeypatch.setattr(
        json,
        "load",
        fake_load
    )



    with pytest.raises(
        IngredientDataError
    ):
        repository = IngredientRepository()
        repository.get_all()
        
