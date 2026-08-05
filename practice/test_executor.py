from src.agent.registry import ToolRegistry
from src.agent.executor import ToolExecutor
from src.agent.tools import IngredientSearchTool
from src.services.ingredient_service import IngredientService
from src.services.ingredient_repository import IngredientRepository
from types import SimpleNamespace


def test_executor():
    repository = IngredientRepository()
    service = IngredientService(repository)

    ingredient_tool = IngredientSearchTool(service)
    registry = ToolRegistry()

    registry.register('search_ingredient',ingredient_tool.search_ingredient)
    executor = ToolExecutor(registry)

    tool_call = SimpleNamespace(function=SimpleNamespace(name = 'search_ingredient',arguments = '{"name": "烟酰胺"}'))
    result = executor.execute(tool_call)
    print(result)
if __name__ == '__main__':
    test_executor()
