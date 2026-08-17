from fastapi import FastAPI
from src.api.ingredient_routes import  router as ingredient_router
from src.api.analyze_routes import router  as analyze_router
from src.api.agent_route import router as agent_router
from src.api.plangate_route import router as gate_router
app = FastAPI()
@app.get("/")
def home():

    return {
        "message":"Beauty-AI API running"
    }





app.include_router(ingredient_router,prefix='/ingredients')
app.include_router(analyze_router,prefix='/analyze')
app.include_router(agent_router,prefix='/agent/chat')
app.include_router(gate_router,prefix='/plangate/choice')