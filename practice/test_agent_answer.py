import json

from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever

from src.agent.rag_tool import RAGTool
from src.agent.registry import ToolRegistry
from src.agent.executor import ToolExecutor
from src.agent.agent import BeautyAgent
from src.agent.session_memory import MemoryStore

from src.ai.llm_client import LLMClient


# =========================================================
# Tool Schema
# =========================================================
# Grounding Validation 当前只开放 search_knowledge，
# 避免其他 Business Tool 干扰本次 RAG Grounding 判断。

search_knowledge_schema = {
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": (
            "从护肤专业知识库中检索与用户问题相关的知识事实。"
            "当用户询问护肤成分的定义、作用、风险、使用方式等专业知识时使用。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "需要检索的护肤专业问题"
                }
            },
            "required": ["query"]
        }
    }
}


# =========================================================
# Observed Executor
# =========================================================

class ObservedExecutor:
    """
    Grounding Validation 专用观察器。

    不改变真实 ToolExecutor 的执行逻辑，
    只额外记录：

    1. Agent 调用了什么 Tool
    2. Tool arguments 是什么
    3. Tool 实际返回了什么
    """

    def __init__(self, executor):
        self.executor = executor
        self.calls = []

    def execute(self, tool_call):

        # 先执行真实 Executor
        result = self.executor.execute(tool_call)

        # 尝试解析 Tool arguments
        try:
            arguments = json.loads(
                tool_call.function.arguments
            )
        except Exception:
            arguments = tool_call.function.arguments

        # 保存本次真实调用
        self.calls.append(
            {
                "tool_name": tool_call.function.name,
                "arguments": arguments,
                "result": result,
            }
        )

        return result


# =========================================================
# Output Helpers
# =========================================================

def print_line():
    print("\n" + "=" * 80)


def print_retrieved_facts(results):

    print("\n[2] ORIGINAL QUERY RETRIEVED TOP3")

    if not results:
        print("No facts retrieved.")
        return

    for index, fact in enumerate(results, start=1):

        print(f"\n--- Top {index} ---")

        print("ID:")
        print(fact.id)

        print("\nIngredient:")
        print(fact.ingredient)

        print("\nCategory:")
        print(fact.category)

        print("\nContent:")
        print(fact.content)

        print("\nSource:")

        for source in fact.source:
            print(
                f"- {source.name}"
                f" | type={source.type}"
                f" | url={source.url}"
            )


def print_tool_calls(observed_executor):

    print("\n[3] BEAUTYAGENT TOOL CALLS")

    if not observed_executor.calls:
        print(
            "\nWARNING: BeautyAgent did not call any tool."
        )
        print(
            "这意味着本次回答没有经过 RAGTool，"
            "不能判定为 RAG Grounding PASS。"
        )
        return

    for index, call in enumerate(
        observed_executor.calls,
        start=1
    ):

        print(f"\n--- Tool Call {index} ---")

        print("\nTool Name:")
        print(call["tool_name"])

        print("\nTool Arguments:")
        print(
            json.dumps(
                call["arguments"],
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        print("\nRAGTool Actual Result:")
        print(
            json.dumps(
                call["result"],
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )


def print_manual_review():

    print_line()

    print("MANUAL GROUNDING REVIEW")

    print_line()

    print(
        """
Grounded Claims:

1.
2.
3.


Unsupported Claims:

1.
2.


Grounding Result:

PASS / FAIL


Reason:



Failure Layer:

NONE

或：

RETRIEVER
RAG_TOOL
PROMPT
BEAUTY_AGENT
LLM_UNSUPPORTED_CLAIM
"""
    )


# =========================================================
# Main
# =========================================================

def main():

    # -----------------------------------------------------
    # 1. Test Query
    # -----------------------------------------------------

    query = "烟酰胺和抗坏血酸有什么区别？"

    print_line()

    print("REAL RAG ANSWER GROUNDING VALIDATION")

    print_line()

    print("\n[1] USER QUERY")

    print("\n" + query)


    # -----------------------------------------------------
    # 2. Build Real Retriever
    # -----------------------------------------------------

    embedding_service = EmbeddingService()

    vector_store = VectorStore()

    vector_store.load()

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        top_k=4,
    )


    # -----------------------------------------------------
    # 3. Direct Retrieval
    #
    # 这里记录：
    #
    # 原始 User Query
    # ↓
    # Retriever
    # ↓
    # Top3
    #
    # 用于和 Runtime Agent 的实际检索进行比较。
    # -----------------------------------------------------

    original_results = retriever.retriever(query)

    print_retrieved_facts(original_results)


    # -----------------------------------------------------
    # 4. Build Real RAGTool
    # -----------------------------------------------------

    rag_tool = RAGTool(
        retriever=retriever
    )


    # -----------------------------------------------------
    # 5. Build Real Registry
    # -----------------------------------------------------

    registry = ToolRegistry()

    registry.register(
        "search_knowledge",
        rag_tool.search_knowledge,
    )


    # -----------------------------------------------------
    # 6. Build Real Executor
    # -----------------------------------------------------

    real_executor = ToolExecutor(
        registry
    )


    # -----------------------------------------------------
    # 7. Add Observer
    # -----------------------------------------------------

    observed_executor = ObservedExecutor(
        real_executor
    )


    # -----------------------------------------------------
    # 8. Build Real LLM
    # -----------------------------------------------------

    llm = LLMClient()


    # -----------------------------------------------------
    # 9. Memory
    # -----------------------------------------------------

    memory_store = MemoryStore()


    # -----------------------------------------------------
    # 10. Build Real BeautyAgent
    # -----------------------------------------------------

    agent = BeautyAgent(
        tools=[
            search_knowledge_schema
        ],
        llm=llm,
        executor=observed_executor,
        memory_store=memory_store,
    )


    # -----------------------------------------------------
    # 11. Run Real Agent
    # -----------------------------------------------------

    session_id = "grounding_function_001"

    print_line()

    print("RUNNING BEAUTYAGENT")

    print_line()

    answer = agent.run(
        session_id=session_id,
        user_input=query,
    )


    # -----------------------------------------------------
    # 12. Actual Runtime RAG Observation
    # -----------------------------------------------------

    print_tool_calls(
        observed_executor
    )


    # -----------------------------------------------------
    # 13. Final Answer
    # -----------------------------------------------------

    print("\n[4] BEAUTYAGENT FINAL ANSWER")

    print("\n" + str(answer))


    # -----------------------------------------------------
    # 14. Manual Grounding Review
    # -----------------------------------------------------

    print_manual_review()


if __name__ == "__main__":
    main()