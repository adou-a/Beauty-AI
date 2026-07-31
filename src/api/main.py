from fastapi import FastAPI
from src.api.ingredient_routes import  router as ingredient_router
from src.api.analyze_routes import router  as analyze_router





app = FastAPI()

app.include_router(ingredient_router,prefix='/ingredients')
app.include_router(analyze_router,prefix='/analyze')
