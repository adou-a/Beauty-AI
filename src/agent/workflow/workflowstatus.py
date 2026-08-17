from src.agent.planning.models import StepStatus
from src.agent.planning.planner import Planner
from enum import Enum

#workflowstatus: status step_states current_step_id  error

class WorkflowStatus(str,Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    

class WorkflowState:

    def __init__(self):
        self.status = WorkflowStatus.PENDING
        self.current_step_id = None
        self.error = None

    def start(self):
        self.status = WorkflowStatus.RUNNING




    def finish(self):
        self.status = WorkflowStatus.COMPLETED
        self.current_step_id = None


   

        



        