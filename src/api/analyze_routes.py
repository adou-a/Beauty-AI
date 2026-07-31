from fastapi import APIRouter
from src.api.schemas import AnalyzeRequest

router = APIRouter()

@router.post('/')
def analyze(request:AnalyzeRequest):
    return{
        'ingredient': request.ingredient,
        'skin-type' : request.skin_type
    }