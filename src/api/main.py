from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.api.ingredient_routes import  router as ingredient_router
from src.api.analyze_routes import router  as analyze_router
from src.api.plangate_route import router as agent_router
from src.api.schemas import ErrorResponse

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def handle_request_validation(
    request: Request, exc: RequestValidationError,
):
    if request.url.path.rstrip("/") == "/agent/chat":
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code="invalid_request", message="Invalid request",
            ).model_dump(),
        )
    return await request_validation_exception_handler(request, exc)


@app.get("/")
def home():

    return {
        "message":"Beauty-AI API running"
    }





app.include_router(agent_router,prefix='/agent/chat')
