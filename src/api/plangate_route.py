from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas import PlangateRequest, PlangateResponse
from src.agent.planning.gate import PlanningGate
from src.api.dependencies import get_gate

from src.utils.logger import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=PlangateResponse)
def gate(
    request: PlangateRequest,
    plangate: PlanningGate = Depends(get_gate),
) -> PlangateResponse:
    try:
        logger.info(
            "Planning gate API request received session=%s",
            request.session_id,
        )
        result = plangate.choice(
            session_id=request.session_id,
            user_input=request.message,
        )


        return PlangateResponse(answer="\n\n".join(result))
    except Exception as exc:
        logger.exception("Planning gate execution failed")
        raise HTTPException(
            status_code=500,
            detail="Planning gate execution failed",
        ) from exc
