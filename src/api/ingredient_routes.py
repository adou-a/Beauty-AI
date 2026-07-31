from  fastapi import APIRouter
from  src.services.ingredient_service import IngredientService
from  src.services.ingredient_repository  import  IngredientRepository

router = APIRouter()
repository = IngredientRepository()
service  = IngredientService(repository)

@router.get('/{name}')

def get_ingredient(name:str):

    result = service.find_ingredient(name)
    return result

    