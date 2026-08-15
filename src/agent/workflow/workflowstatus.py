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

    def __init__(self,step_ids):
        self.status = WorkflowStatus.PENDING
        self.step_states = {step_id: StepStatus.PENDING for step_id in  step_ids}
        self.current_step_id = None
        self.error = None

    def start(self):
        self.status = WorkflowStatus.RUNNING


    def start_step(self,step_id):
    
        self.current_step_id = step_id
        self.step_states[step_id] = StepStatus.RUNNING

    def fail(self,step_id,error):
        self.status = WorkflowStatus.FAILED
        self.current_step_id = step_id
        self.step_states[step_id ] = StepStatus.FAILED
        self.error = error


    def finish(self):
        self.status = WorkflowStatus.COMPLETED
        self.current_step_id = None


   

        



        