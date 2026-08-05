from src.services.ingredient_service import IngredientService


class IngredientSearchTool:

    def __init__(self,service:IngredientService):
        self.serivice = service

    def search_ingredient(self,name:str):

        ingredient = (self.serivice.find_ingredient(name))


        return ingredient