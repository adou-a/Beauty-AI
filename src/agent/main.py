from src.agent.agent import BeautyAgent
from src.agent.registry import ToolRegistry
from src.ai.llm_client import LLMClient
from src.agent.tools import IngredientSearchTool
from src.agent.schemas import ingredient_tool_schema
from src.services.ingredient_repository import IngredientRepository
from src.services.ingredient_service import IngredientService
from src.agent.executor import ToolExecutor

def create_agent():
    
    repository = IngredientRepository()
    service = IngredientService(repository)
    tool = IngredientSearchTool(service)
    registry = ToolRegistry()

    registry.register('search_ingredient',tool.search_ingredient)
    executor = ToolExecutor(registry)

    llm = LLMClient()

    tools = [ingredient_tool_schema]


    agent = BeautyAgent(tools=tools,llm=llm,executor=executor)
    return agent


agent = create_agent()