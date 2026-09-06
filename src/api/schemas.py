from pydantic import BaseModel, field_validator



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


class AnalyzeRequest(BaseModel):

    ingredient: str


class Suitable_type(BaseModel):
    ingredient: str
    check_skin_type: str



class AgentRequest(BaseModel):
    session_id: str
    message: str

    @field_validator("session_id", "message")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")
        return value


class AgentResponse(BaseModel):

    answer: str

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")
        return value


class ErrorResponse(BaseModel):
    code: str
    message: str
