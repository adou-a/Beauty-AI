from pydantic import BaseModel

class  IngredientAnalysis(BaseModel):
    ingredient: str
    benefits: list[str]
    suitable_skin_types: list[str]
    risks: str
    suggestion: str