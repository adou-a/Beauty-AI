from src.api.schemas import AgentRequest,AgentResponse
from src.exceptions.agent_exception import AgentExecutionError
from src.utils.logger import get_logger
from src.api.dependencies import get_agent
from fastapi import APIRouter,Depends,HTTPException
from src.agent.agent import BeautyAgent

router = APIRouter()

logger = get_logger(__name__)

@router.post('/',response_model=AgentResponse)
def chat(request:AgentRequest,agent: BeautyAgent = Depends(get_agent)):
    try:
        logger.info('Agent API request received session=%s',request.session_id)
        result =  agent.run(request.session_id,request.message)
        return {'answer': result}

    except AgentExecutionError:
        logger.exception('Agent execution failed')
        raise HTTPException(status_code= 500,detail= 'Agent execution failed')