from src.models.ingredient import Ingredient
def test_create_ingredient():

    ingredient = Ingredient(
        id=1,
        inci_name="Niacinamide",
        chinese_name="烟酰胺",
        category="美白修护",
        functions=["改善肤色"],
        suitable_skin_types=["油皮"],
        avoid_skin_types=[],
        risk_level="低",
        description="测试"
    )

    assert ingredient.chinese_name == "烟酰胺"