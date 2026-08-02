from src.services.ingredient_service import IngredientService
from src.ai.ai_response import IngredientAnalysis
from src.ai.llm_client import LLMClient
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
    def ingredient_suitable_types(self,name:str,skin_type:str):
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
请根据一下成分资料回答用户问题
{context}
请严格返回：
{name}主要作用：
适合的肤质和注意事项


'''       
        result = self.client.chat(prompt)
        return result
        

        



    