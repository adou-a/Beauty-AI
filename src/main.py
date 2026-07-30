#功能1：获取所有成分
#功能2：根据名字查询
#功能3：根据功效查询
from src.services.ingredient_repository import IngredientRepository
from src.services.ingredient_service  import IngredientService
repository = IngredientRepository()
service = IngredientService(repository)

ingredient = input('what name do you want to konw? ' )
category  =input('what effect do you want to check? ')
result1 =service.total_ingredients()
result2 = service.find_ingredient(ingredient)
print(result2)
result3 = service.find_by_category(category)
print(result3)
