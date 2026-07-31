from pydantic import BaseModel



class IngredientResponse(BaseModel):

    id: int
    inci_name: str
    chinese_name: str
    category: str
    functions: list[str]
    risk_level: str
    description: str
    suitable_skin_types: list[str]
    avoid_skin_types: list[str]