from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from openai import APIConnectionError, APIStatusError

from src.api.schemas import AgentRequest, AgentResponse, ErrorResponse
from src.agent.planning.gate import PlanningGate
from src.api.dependencies import get_gate

from src.utils.logger import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/",
    response_model=AgentResponse,
    responses={status: {"model": ErrorResponse} for status in (422, 503, 500)},
)
def chat(
    request: AgentRequest,
    plangate: PlanningGate = Depends(get_gate),
) -> AgentResponse | JSONResponse:
    try:
        logger.info(
            "Agent API request received session=%s", 
            request.session_id,
        )
        result = plangate.choice(
            session_id = request.session_id,
            user_input = request.message,
        )


        return AgentResponse(answer = result)
    except (APIConnectionError, APIStatusError):
        logger.exception("Agent dependency unavailable")
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                code="service_unavailable",
                message="Service temporarily unavailable",
            ).model_dump(),
        )
    except Exception:
        logger.exception("Agent execution failed")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code="internal_error", message="Internal server error",
            ).model_dump(),
        )
