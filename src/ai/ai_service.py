from .llm_client import LLMClient
from ..services.ingredient_service import IngredientService


class AIService:

    def __init__(
        self,
        llm_client: LLMClient,
        ingredient_service: IngredientService
    ) -> None:

        self.llm_client = llm_client
        self.ingredient_service = ingredient_service


    def analyze_ingredient(
        self,
        name: str
    ) -> str:

        ingredient = self.ingredient_service.find_ingredient(name)

        if ingredient is None:
            return "没有找到该成分"

        prompt = f"""
        分析这个护肤成分：

        名称:
        {ingredient.chinese_name}

        功效:
        {ingredient.functions}

        风险:
        {ingredient.risk_level}
        """

        return self.llm_client.generate(prompt)