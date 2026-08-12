from enum import Enum
from dataclasses import dataclass,field
#规定step status的状态值
class StepStatus(str,Enum):
    #等待中，任务创建还未执行
    PENDING = 'pending'
    #任务正在执行中
    RUNNING = 'running'
    #任务已完成
    COMPLETED = 'completed'
    #任务执行失败
    FAILED = 'failed'



@dataclass
class PlanStep:

    id: int

    description: str
    #未提供状态，默认为PENDING
    status: StepStatus = StepStatus.PENDING

    result: str | None = None



@dataclass
class Plan:

    goal: str
    #创造一个plan，如果没有提供step就给他一个列表
    steps: list[PlanStep] = field(default_factory = list)