from src.services.ingredient_service import IngredientService


class IngredientSearchTool:

    def __init__(self,service:IngredientService):
        self.serivice = service

    def search_ingredient(self,name:str):

        ingredient = (self.serivice.find_ingredient(name))


        return ingredient


    def check_skin_risk(self,skin_type:str):

        return{
            'skin_type': skin_type,
            'risk': '需要注意刺激性'
        }