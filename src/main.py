from src.agent.agent import BeautyAgent
from src.ai.llm_client import LLMClient
from src.agent.registry import ToolRegistry
from src.agent.session_memory import MemoryStore
from src.agent.tools import IngredientSearchTool
from src.agent.rag_tool import RAGTool
from src.agent.executor import ToolExecutor
from src.api.dependencies import get_ingredient_service
from src.agent.schemas import (ingredient_tool_schema,search_knowledge_schema,search_ingredient_schema)
from src.rag.retriever import Retriever
from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
from src.agent.planning.models import Plan,PlanStep
from src.agent.planning.plan_executor import PlanExecutor
from src.agent.planning.agent_step_executor import AgentStepExecutor
ingredient_service = get_ingredient_service()
tool = IngredientSearchTool(ingredient_service)


llm =LLMClient()


memory_store  = MemoryStore()
embedding_service = EmbeddingService()
vector_store = VectorStore()
vector_store.load()
retriever = Retriever(embedding_service = embedding_service,vector_store = vector_store,top_k = 3)
rag_tool =RAGTool(retriever)
registry = ToolRegistry()
registry.register('search_ingredient',tool.search_ingredient)
registry.register('check_skin_risk',tool.check_skin_risk)
registry.register('search_knowledge',rag_tool.search_knowledge)
tools = [ingredient_tool_schema,search_ingredient_schema,search_knowledge_schema]
executor = ToolExecutor(registry)

agent  = BeautyAgent(tools = tools,llm = llm,executor = executor,memory_store = memory_store)
plan = Plan(
    goal="为敏感肌用户制定视黄醇耐受方案",
    steps=[
        PlanStep(
            id=1,
            description=(
                "获取视黄醇的基础作用和刺激风险信息"
            ),
        ),
        PlanStep(
            id=2,
            description=(
                "分析敏感肌使用视黄醇的风险"
            ),
        ),
        PlanStep(
            id=3,
            description=(
                "检索视黄醇建立耐受的相关专业知识"
            ),
        ),
    ],
)


step_executor = AgentStepExecutor(
    agent=agent,
    session_id="phase6-day4-real",
    goal=plan.goal,
)


plan_executor = PlanExecutor(
    step_executor=step_executor,
)


completed_plan = (
    plan_executor.execute(
        plan
    )
)


for step in completed_plan.steps:

    print(
        "\nStep:",
        step.id,
    )

    print(
        "Description:",
        step.description,
    )

    print(
        "Status:",
        step.status,
    )

    print(
        "Result:",
        step.result,
    )