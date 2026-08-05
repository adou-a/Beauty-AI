from src.agent.tools import IngredientTool

tools = IngredientTool(service)

result = tools.search_ingredient('烟酰胺')
print(result)