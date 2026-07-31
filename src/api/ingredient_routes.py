from  fastapi import APIRouter
from fastapi import Depends
from  src.services.ingredient_service import IngredientService
from  src.api.dependencies import get_ingredient_service
from  fastapi import HTTPException
from  src.exceptions.ingredient_exception import IngredientDataError

router = APIRouter()


@router.get('/{name}')

def get_ingredient(name:str,service:IngredientService = Depends(get_ingredient_service)):
    try:
        result = service.find_ingredient(name)
    except IngredientDataError:
        raise HTTPException(status_code=500, detail='ingredient database error')
    if not result:
        raise HTTPException(status_code=404, detail= 'ingredient not found')
    return result

