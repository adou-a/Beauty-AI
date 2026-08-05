class AgentError(Exception):
    pass


class ToolNotFoundError(AgentError):
    pass


class ToolExecutionError(AgentError):
    pass