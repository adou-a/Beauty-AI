from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from openai import APIConnectionError, APIStatusError
from src.api.plangate_route import router as agent_router
from src.api.schemas import ErrorResponse
from src.config import settings
from src.rag.vector_store import VectorStore
from src.utils.logger import get_logger


logger = get_logger(__name__)

#在fastapi启动前检查vector_store的存在情况
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    try:
        settings.check_settings()
    except ValueError as exc:
        raise RuntimeError(
            "DEEPSEEK_API_KEY startup validation failed: "
            "DEEPSEEK_API_KEY is missing or blank"
        ) from exc

    vector_store = VectorStore()
    try:
        vector_store.load_required()
    except Exception as exc:
        logger.error(
            "Vector store startup validation failed",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        raise RuntimeError(
            "Vector store startup validation failed: "
            f"{vector_store.storage_path}"
        ) from exc
    yield


app = FastAPI(lifespan = lifespan)
 

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


@app.exception_handler(APIConnectionError)
@app.exception_handler(APIStatusError)
async def handle_service_unavailable(
    _request: Request,
    exc: APIConnectionError | APIStatusError,
) -> JSONResponse:
    logger.error(
        "Agent dependency unavailable",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(
            code="service_unavailable",
            message="Service temporarily unavailable",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def handle_unexpected_exception(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "Unhandled application exception",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code="internal_error",
            message="Internal server error",
        ).model_dump(),
    )


@app.get("/")
def home():

    return {
        "message":"Beauty-AI API running"
    }





app.include_router(agent_router,prefix='/agent/chat')
