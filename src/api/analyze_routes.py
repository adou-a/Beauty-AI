from src.api.dependencies import get_ai_service
from src.api.schemas import AnalyzeRequest
from src.ai.ai_service import AIService
from fastapi import APIRouter,Depends

router = APIRouter()

@router.post('/')
def analyze(request:AnalyzeRequest,ai_service:AIService = Depends(get_ai_service)):


    result = ai_service.analyze_ingrdient(request.ingredient)
    return result
 