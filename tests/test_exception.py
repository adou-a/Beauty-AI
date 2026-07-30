import pytest

from src.services.ingredient_repository import IngredientRepository
from src.exceptions.ingredient_exception import IngredientDataError


from src.services.ingredient_service import IngredientService

from src.exceptions.ingredient_exception import IngredientNotFoundError

def test_database_error():

    with pytest.raises(IngredientDataError):

        raise IngredientDataError(
            "测试异常"
        )




def test_ingredient_not_found():

    repository = IngredientRepository()

    service = IngredientService(repository)

    with pytest.raises(IngredientNotFoundError):

        service.find_ingredient("不存在成分")