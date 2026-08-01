from src.ai.llm_client import LLMClient
from src.services.ingredient_service import IngredientService




class AIService:
    def __init__(self,ingredient_service: IngredientService,llm_client:LLMClient):
        self.client = llm_client
        self.ingredient_service = ingredient_service


    def analyze_ingrdient(self,name:str) -> str:

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
    请根据一下数据库信息分析：
    {context}

    用户想了解成分：
    {name}
    输出：
    1.成分作用
    2.适合肤质
    3.使用注意
    4.简单建议

    控制在300字以内

'''



    
        response = self.client.chat(prompt)
        return response



    