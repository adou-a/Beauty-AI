from pydantic import BaseModel,ConfigDict


class ValidationOutput(BaseModel):

    model_config = ConfigDict(
        strict = True,extra = 'forbid'
    )
    success: bool
    reasons: list[str]
    
    



class ValidationResult(BaseModel):
    success: bool
    reasons: list[str]