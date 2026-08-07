from src.api.schemas import AgentRequest,AgentResponse
from src.exceptions.agent_exception import AgentExecutionError
from src.api.dependencies import get_agent
from fastapi import APIRouter,Depends,HTTPException
from src.agent.agent import BeautyAgent

router = APIRouter()



@router.post('/',response_model=AgentResponse)
def chat(request:AgentRequest,agent: BeautyAgent = Depends(get_agent)):
    try:
        result =  agent.run(request.session_id,request.message)
        return {'answer': result}

    except AgentExecutionError:
        raise HTTPException(status_code= 500,detail= 'Agent execution failed')