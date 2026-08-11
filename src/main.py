from src.agent.agent import BeautyAgent
from src.ai.llm_client import LLMClient
from src.agent.registry import ToolRegistry
from src.agent.session_memory import MemoryStore
from src.agent.tools import IngredientSearchTool
from src.agent.rag_tool import RAGTool
from src.agent.executor import ToolExecutor
from src.api.dependencies import get_ingredient_service
from src.agent.schemas import (ingredient_tool_schema,search_knowledge_schema,search_ingredient_schema)
from src.rag.retriever import Retriever
from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
ingredient_service = get_ingredient_service()
tool = IngredientSearchTool(ingredient_service)


llm =LLMClient()


memory_store  = MemoryStore()
embedding_service = EmbeddingService()
vector_store = VectorStore()
vector_store.load()
retriever = Retriever(embedding_service = embedding_service,vector_store = vector_store,top_k = 3)
rag_tool =RAGTool(retriever)
registry = ToolRegistry()
registry.register('search_ingredient',tool.search_ingredient)
registry.register('check_skin_risk',tool.check_skin_risk)
registry.register('search_knowledge',rag_tool.search_knowledge)
tools = [ingredient_tool_schema,search_ingredient_schema,search_knowledge_schema]
executor = ToolExecutor(registry)

agent  = BeautyAgent(tools = tools,llm = llm,executor = executor,memory_store = memory_store)
session_id = '002'
user_input = ('我是敏感肌,最近开始使用视黄醇,有一点脱皮和刺痛,这种情况正常吗,需要注意什么？')



result =  agent.run(session_id  = session_id,user_input = user_input)
print(result)