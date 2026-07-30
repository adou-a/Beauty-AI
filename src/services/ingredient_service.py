from .ingredient_repository import IngredientRepository
from ..models.ingredient import Ingredient
from ..utils.logger import get_logger

logger = get_logger(__name__)
class IngredientService:
    def __init__(self,repository: IngredientRepository):
        self.repository = repository


    def find_ingredient(self,name:str) -> Ingredient | None:
        logger.info(f'Searching ingredient: {name}')
        
        ingredients = self.repository.get_all()
        
        for ingredient in ingredients:
            if  name == ingredient.chinese_name:
                logger.info(f'Found ingredient: {name}')
                return ingredient
        logger.warning(f'Ingredient not found: {name}')      
        return None
        

        
       

    def total_ingredients(self) -> list[Ingredient]:
        return self.repository.get_all()

    def find_by_category(self,category:str) -> list[Ingredient]:
        logger.info(f'Searching ingredients by category: {category}')
        ingredients = self.repository.get_all()

        result = []

        for ingredient in ingredients:
            if  category in ingredient.category:
                result.append(ingredient)
        logger.info(f'Found {len(result)} ingredients')
        return result

    def find_by_function(self,function:str) -> list[Ingredient]:
        logger.info(f'Searching ingredients by function: {function}')
        ingredients = self.repository.get_all()
        result = []

        for  ingredient in ingredients:
            if function in ingredient.functions:
                result.append(ingredient)
        logger.info(f'Found {len(result)} ingredients')
        return result

    def find_by_skin_type(self,skin_type:str) -> list[Ingredient]:
        logger.info(f'Searching skin type:{skin_type}')
        ingredients = self.repository.get_all()

        result = []
        for  ingredient in ingredients:
            if skin_type in ingredient.suitable_skin_types:
                result.append(ingredient)
        logger.info(f'Found {len(result)} ingredients')
        return result

    

                


            
