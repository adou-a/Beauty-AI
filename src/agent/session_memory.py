from  src.agent.memory import ConversationMemory
from  src.utils.logger import get_logger

logger = get_logger(__name__)
class MemoryStore:


    def __init__(self):
        self.sessions = {}


    def get_memory(self,session_id:str):


        if session_id not in self.sessions:
            logger.info("Create new session: %s",session_id)
            self.sessions[session_id] = ConversationMemory()

        else:
            logger.info('Load existing session: %s', session_id)
        return self.sessions[session_id]