from  fastapi import APIRouter
from fastapi import Depends
from  src.services.ingredient_service import IngredientService
from  src.api.dependencies import get_ingredient_service

router = APIRouter()


@router.get('/{name}')

def get_ingredient(name:str,service:IngredientService = Depends(get_ingredient_service)):

    result = service.find_ingredient(name)
    return result

    