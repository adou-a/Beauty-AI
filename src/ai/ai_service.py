from src.ai.llm_client import LLMClient
from src.services.ingredient_service import IngredientService
from src.ai.ai_response import IngredientAnalysis
import json



class AIService:
    def __init__(self,ingredient_service: IngredientService,llm_client:LLMClient):
        self.client = llm_client
        self.ingredient_service = ingredient_service


    def analyze_ingrdient(self,name:str) -> IngredientAnalysis:

        ingredient = self.ingredient_service.find_ingredient(name)
        if ingredient is None:
            return '没有找到该成分'


        context = f'''
成分信息：
中文名称：
{ingredient.chinese_name}

INCI名称:
{ingredient.inci_name}

种类:
{ingredient.category}

作用：
{ingredient.functions}

描述：
{ingredient.description}

适合肤质：
{ingredient.suitable_skin_types}

风险：
{ingredient.risk_level}

'''    
        prompt = f'''
根据以下成分数据库：
{context}


请严格返回JSON 格式
{{
'ingredient': '',
'benefits': [],
'suitable_skin_types': [],
'risks': '',
'suggestion':''
}}


'''
        response = self.client.chat(prompt)
       
        data = json.loads(response)
        analysis = IngredientAnalysis(**data)

        return analysis



    