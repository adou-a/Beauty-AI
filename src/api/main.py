from fastapi import FastAPI
from src.services.ingredient_repository import IngredientRepository
from src.services.ingredient_service import IngredientService


app = FastAPI()
repository = IngredientRepository()
service = IngredientService(repository)



@app.get('/')
def home():
    return{
         "name":"niacinamide"
     
    }

@app.get('/ingredients/{name}')
def get_ingredient(name:str):

    ingredient = service.find_ingredient(name)

    if ingredient is None:
        return{'message':'ingredient not found'}

    return ingredient