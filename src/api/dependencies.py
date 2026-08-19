from src.agent.schemas import (
    ingredient_tool_schema,
    search_ingredient_schema,
    search_knowledge_schema,
)
from src.services.ingredient_repository import IngredientRepository
from src.services.ingredient_service import IngredientService
from src.agent.tools import IngredientSearchTool
from src.agent.rag_tool import RAGTool
from src.agent.registry import ToolRegistry
from src.agent.executor import ToolExecutor
from src.agent.agent import BeautyAgent
from src.ai.ai_service import AIService
from src.ai.llm_client import LLMClient
from src.agent.session_memory import MemoryStore
from src.agent.planning.agent_step_executor import AgentStepExecutor
from src.agent.planning.gate import PlanningGate
from src.agent.planning.plan_executor import PlanExecutor
from src.agent.planning.planner import Planner
from src.agent.validation.validator import Validator
from src.agent.workflow.final_answer import FinalAnswer
from src.agent.workflow.workflowrunner import WorkflowRunner
from src.rag.embedding import EmbeddingService
from src.rag.retriever import Retriever
from src.rag.vector_store import VectorStore

def get_ingredient_service():
    respository = IngredientRepository()
    return IngredientService(respository)



def get_llm_client():
    return LLMClient()

def get_ai_service():
    ingredient_service = get_ingredient_service()
    llm = LLMClient()
    return AIService(ingredient_service,llm)


def get_agent():
    ingredient_service = get_ingredient_service()
    ingredient_tool = IngredientSearchTool(ingredient_service)

    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    vector_store.load()
    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        top_k=3,
    )
    rag_tool = RAGTool(retriever)

    registry = ToolRegistry()
    registry.register("search_ingredient", ingredient_tool.search_ingredient)
    registry.register("check_skin_risk", ingredient_tool.check_skin_risk)
    registry.register("search_knowledge", rag_tool.search_knowledge)

    return BeautyAgent(
        tools=[
            ingredient_tool_schema,
            search_ingredient_schema,
            search_knowledge_schema,
        ],
        llm=get_llm_client(),
        executor=ToolExecutor(registry),
        memory_store=MemoryStore(),
    )


def get_gate():
    llm = get_llm_client()
    agent = get_agent()
    planner = Planner(llm=llm)
    step_executor = AgentStepExecutor(agent=agent)
    plan_executor = PlanExecutor(step_executor=step_executor)
    final_answer = FinalAnswer(llm=llm)
    validator = Validator(llm=llm)
    workflow_runner = WorkflowRunner(
        planner=planner,
        planexecutor=plan_executor,
        final_answer=final_answer,
        validator=validator,
    )

    return PlanningGate(
        llm=llm,
        agent=agent,
        workflow_runner=workflow_runner,
    )
