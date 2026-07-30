from pathlib import Path
import json
from ..models.ingredient import Ingredient
from ..exceptions.ingredient_exception import IngredientDataError
from ..utils.logger import get_logger



logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_PATH = BASE_DIR/'data'/'ingredients.json'


class IngredientRepository:
    def __init__(self) -> None:
        try:
            with open(DATA_PATH,'r',encoding='utf-8') as file:
                data  = json.load(file)

        except FileNotFoundError:
            raise IngredientDataError('成分数据库文件不存在')
        except json.JSONDecodeError:
            raise IngredientDataError('成分数据库格式错误')

        self.ingredients = []

        for item in data:

            ingredient = Ingredient(
                id = item['id'],
                inci_name = item['inci_name'],
                chinese_name = item['chinese_name'],
                category = item['category'],
                functions = item['functions'],
                suitable_skin_types = item['suitable_skin_types'],
                avoid_skin_types = item['avoid_skin_types'],
                risk_level = item['risk_level'],
                description = item['description']
            )

            self.ingredients.append(ingredient)
        logger.info(
f"Loaded {len(self.ingredients)} ingredients"
)


    def get_all(self) -> list[Ingredient]:
        return self.ingredients


   

                                                 

