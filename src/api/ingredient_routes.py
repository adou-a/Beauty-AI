from  src.exceptions.ingredient_exception import IngredientDataError
from  src.services.ingredient_service import IngredientService
from  src.api.dependencies import get_ingredient_service
from  fastapi import HTTPException
from  fastapi import APIRouter
from fastapi import Depends

router = APIRouter()


@router.get('/{name}')

def get_ingredient(name:str,service:IngredientService = Depends(get_ingredient_service),summary = '查询护肤成分',description ='根据中文名称查询成分信息'):
    try:
        result = service.find_ingredient(name)
    except IngredientDataError:
        raise HTTPException(status_code=500, detail='ingredient database error')
    if not result:
        raise HTTPException(status_code=404, detail= 'ingredient not found')
    return result

