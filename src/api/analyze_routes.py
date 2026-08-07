from src.api.dependencies import get_ai_service
from src.api.schemas import AnalyzeRequest,Suitable_type
from src.ai.ai_service import AIService
from fastapi import APIRouter,Depends

router = APIRouter()

@router.post('/')
def analyze(request:AnalyzeRequest,ai_service:AIService = Depends(get_ai_service)):


    result = ai_service.analyze_ingrdient(request.ingredient)
    return result


@router.post('/suitable_type')
def ingredient_suitable_type(ingredient,check_skin_type:Suitable_type ,ai_service: AIService = Depends(get_ai_service)):

    result = ai_service.ingredient_suitable_types(ingredient,check_skin_type)
    return result




