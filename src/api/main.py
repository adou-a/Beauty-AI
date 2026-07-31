from fastapi import FastAPI
from src.services.ingredient_repository import IngredientRepository
from src.services.ingredient_service import IngredientService
from src.api.schemas import IngredientResponse

app = FastAPI()
repository = IngredientRepository()
service = IngredientService(repository)



@app.get('/')
def home():
    return{
         "name":"niacinamide"
     
    }

@app.get('/ingredients/{name}',response_model= IngredientResponse)
def get_ingredient(name:str):

    ingredient = service.find_ingredient(name)


    return ingredient