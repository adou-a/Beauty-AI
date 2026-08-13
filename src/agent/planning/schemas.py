from pydantic import BaseModel, Field



#LLM的结构化输出
class PlanStepOutput(BaseModel):

    description: str = Field(min_length = 1)


#规范LLM的结构化回答
class PlanOutput(BaseModel):

    goal: str = Field(min_length = 1)
    #最少一步，最多八步
    steps: list[PlanStepOutput] = Field(min_length = 1,max_length = 8)