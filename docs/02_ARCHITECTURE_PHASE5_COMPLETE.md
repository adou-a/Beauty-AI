# Beauty-AI Architecture

# 当前整体架构

```text
Client
  |
  v
FastAPI
  |
  v
Router
  |
  v
Dependency Injection
  |
  v
BeautyAgent
  |
  +-----------------------------+
  |                             |
  v                             v
Memory                       LLMClient
                                |
                                v
                             DeepSeek
                                |
                                v
                           Tool Calling
                                |
                                v
                          Tool Executor
                                |
                                v
                          Tool Registry
                                |
          +---------------------+---------------------+
          |                     |                     |
          v                     v                     v
 search_ingredient       check_skin_risk      search_knowledge
          |                                           |
          v                                           v
 IngredientService                                  RAGTool
          |                                           |
          v                                           v
 IngredientRepository                             Retriever
          |                                           |
          v                                  +--------+--------+
 ingredients.json                           |                 |
                                           v                 v
                                  EmbeddingService      VectorStore
                                                            |
                                                            v
                                                     Knowledge Base
```

# 当前请求流程

```text
1. User 输入问题
2. FastAPI 接收请求
3. Router 处理 HTTP
4. Dependency Injection 提供 BeautyAgent
5. Agent 加载 Conversation Context
6. Agent 调用 LLMClient
7. DeepSeek 根据用户目标和可用 Tool Schema 决定是否调用工具
8. DeepSeek 返回一个或多个 tool_call
9. ToolExecutor 解析工具名称与 arguments
10. ToolRegistry 查找对应 Tool
11. ToolExecutor 执行 Tool
12. Tool Result 作为 Observation 返回 Agent
13. Agent 将 Observation 加入 messages
14. Agent 再次调用 DeepSeek
15. 如果仍有 tool_calls，则继续 Agent Loop
16. 无 tool_call 时返回 Final Answer
```

如果 DeepSeek 选择：

```text
search_ingredient
```

则执行：

```text
search_ingredient
 ↓
IngredientService
 ↓
IngredientRepository
 ↓
ingredients.json
```

如果 DeepSeek 选择：

```text
search_knowledge
```

则执行：

```text
search_knowledge
 ↓
RAGTool
 ↓
Retriever
 ↓
EmbeddingService
 ↓
Query Vector
 ↓
VectorStore
 ↓
Similarity Search
 ↓
Top K Relevant Chunks
 ↓
Context / Sources
 ↓
Tool Observation
 ↓
BeautyAgent
 ↓
DeepSeek
 ↓
Final Answer
```

# RAG 架构

## Offline / Indexing Pipeline

建立或更新知识库时运行：

```text
data/knowledge/*.md
        ↓
DocumentLoader
        ↓
Document
        ↓
TextChunker
        ↓
Chunk
        ↓
EmbeddingService
        ↓
EmbeddedChunk
        ↓
KnowledgeIndexer
        ↓
VectorStore
        ↓
vector_store.json / Persistence
```

职责：

```text
原始文档
↓
转换为可检索知识索引
```

这条链路不应该在每次用户 Query 时重新完整执行。

---

## Online / Retrieval Pipeline

用户查询时运行：

```text
Natural Language Query
        ↓
Retriever
        ↓
EmbeddingService
        ↓
Query Vector
        ↓
VectorStore.search()
        ↓
Cosine Similarity
        ↓
Score Ranking
        ↓
Top K SearchResult
```

Retriever 对上层隐藏：

- Embedding 调用细节
- Vector 细节
- Similarity Search 细节
- Top K 检索细节

调用方只需要：

```python
results = retriever.retrieve(query)
```

---

## Independent RAG Pipeline

Phase 5 Day 6 完成的独立 RAG：

```text
Question
 ↓
Retriever
 ↓
Relevant SearchResults
 ↓
build_context()
 ↓
Context Injection
 ↓
LLMClient
 ↓
DeepSeek
 ↓
RAG Answer
```

这个链路用于验证：

```text
Retrieval + Context + Generation
```

能够独立工作。

---

## Agent + RAG Pipeline

接入 BeautyAgent 后，不让 RAG Tool 再单独完成最终生成。

正确：

```text
BeautyAgent
 ↓
DeepSeek
 ↓
search_knowledge
 ↓
RAGTool
 ↓
Retriever
 ↓
Relevant Context
 ↓
Tool Observation
 ↓
BeautyAgent
 ↓
DeepSeek
 ↓
Final Answer
```

避免：

```text
Agent DeepSeek
↓
RAGService DeepSeek
↓
Agent DeepSeek
```

产生不必要的重复 LLM 调用。

# 当前项目结构

```text
src
│
├── agent
│   ├── agent.py
│   ├── executor.py
│   ├── registry.py
│   ├── schemas.py
│   ├── tools.py
│   ├── rag_tool.py
│   └── session_memory.py
│
├── ai
│   ├── llm_client.py
│   └── ai_service.py
│
├── api
│   ├── main.py
│   ├── agent_routes.py
│   ├── ingredient_routes.py
│   ├── schemas.py
│   └── dependencies.py
│
├── rag
│   ├── __init__.py
│   ├── models.py
│   ├── loader.py
│   ├── chunker.py
│   ├── embedding.py
│   ├── similarity.py
│   ├── vector_store.py
│   ├── indexer.py
│   ├── retriever.py
│   └── rag_service.py
│
├── services
│   ├── ingredient_repository.py
│   └── ingredient_service.py
│
├── models
├── exceptions
├── config
└── utils
```

# 模块职责

## API Layer

负责：

- HTTP 请求
- 参数验证
- Response
- Router
- Dependency Injection
- HTTP Exception
- Swagger

不负责：

- Agent 决策
- RAG 检索逻辑
- Service 业务逻辑

---

## BeautyAgent

负责：

- 接收用户目标
- Conversation Context
- Agent Loop
- messages
- 调用 LLMClient
- 判断 tool_calls
- 将 Observation 加入 messages
- 控制继续执行或返回

核心：

```text
Think → Act → Observe → Think → Answer
```

BeautyAgent 不应该直接依赖：

```text
VectorStore
EmbeddingService
Cosine Similarity
```

这些属于 RAG 底层能力。

---

## LLMClient

默认模型：**DeepSeek**

负责：

- DeepSeek API
- messages
- tools schema
- tool_calls / content
- 模型配置
- LLM Exception
- LLM Logging

原则：

```text
LLMClient 只负责模型通信
```

---

## Tool Schema

文件：

```text
src/agent/schemas.py
```

当前告诉 DeepSeek 的主要 Tools：

```text
search_ingredient
check_skin_risk
search_knowledge
```

Schema 负责：

- Tool 名称
- Tool 描述
- 参数结构
- 参数类型
- required

Schema 不负责执行函数。

---

## Tool Registry

文件：

```text
src/agent/registry.py
```

负责：

```text
register
get
get_tools
exists
```

作用：

让 Agent 与具体函数实现解耦。

---

## Tool Executor

文件：

```text
src/agent/executor.py
```

负责：

```text
tool_call
 ↓
function.name
 ↓
function.arguments
 ↓
Registry
 ↓
Tool
 ↓
Result
```

原则：

```text
Agent 决定做什么
Executor 负责怎么执行
```

---

## Business Tool Layer

### search_ingredient

```text
search_ingredient
 ↓
IngredientService
 ↓
IngredientRepository
 ↓
ingredients.json
```

适合：

```text
结构化、明确的成分查询
```

### check_skin_risk

根据肤质提供基础风险提示。

适合：

```text
基础肤质风险能力
```

---

## RAG Tool Layer

### search_knowledge

```text
search_knowledge
 ↓
RAGTool
 ↓
Retriever
```

职责：

```text
从非结构化知识库检索与用户问题相关的专业资料
```

RAG Tool 返回：

- Context
- Source
- Relevant Knowledge

不负责最终回答生成。

---

## DocumentLoader

负责：

```text
Knowledge Markdown
↓
Document
```

主要保留：

- content
- source

---

## TextChunker

负责：

```text
Document
↓
Chunks
```

核心参数：

```text
chunk_size
overlap
```

Overlap 用于降低重要上下文刚好被切断的风险。

---

## EmbeddingService

负责：

```text
Text
↓
Embedding Model
↓
Vector
```

知识库 Chunk 与 Query 需要处于相同的 Embedding 表示空间，才能进行有效向量比较。

---

## VectorStore

当前实现：

```text
Local VectorStore + JSON Persistence
```

负责：

- 保存 EmbeddedChunk
- 保存 content / source / index / vector
- save / load
- Similarity Search
- Top K

当前实现主要用于学习并验证底层机制，不代表已经是生产级 Vector Database。

---

## KnowledgeIndexer

负责组织：

```text
Loader
+
Chunker
+
EmbeddingService
+
VectorStore
```

建立完整知识索引。

原则：

```text
Indexer 负责协调
不重新实现各组件内部逻辑
```

---

## Similarity Layer

当前使用：

```text
Cosine Similarity
```

作用：

```text
Query Vector
↕
Chunk Vector
↓
Similarity Score
```

然后：

```text
Score Ranking
↓
Top K
```

注意：

```text
Top K ≠ 一定相关
```

Top K 只表示当前知识库里排名最高的 K 个结果。

---

## Retriever

输入：

```text
Natural Language Query
```

输出：

```text
list[SearchResult]
```

职责：

```text
Question
↓
Embedding
↓
Vector Search
↓
Relevant Knowledge
```

Retriever 是面向 RAG 的检索抽象层。

---

## RAGService

独立 RAG Pipeline 的上层协调组件。

负责：

```text
Retriever
↓
Context
↓
LLMClient
↓
Answer
```

用于独立验证完整 RAG，不作为 Agent 场景中每次 `search_knowledge` 的内部第二层 LLM。

---

## Memory Layer

当前完成：

- Short-term Conversation Memory
- Session Context

未来：

- Persistent Memory
- User Profile
- Long-term Memory

---

## Testing Layer

Phase 4：

```text
FakeLLM Testing
```

Phase 5 增加：

```text
FakeEmbeddingService
VectorStore Unit Test
Retriever Test
RAG Tool Test
Agent + RAG Behavior Test
Regression Testing
```

原则：

```text
Unit Test 隔离不稳定外部依赖
Integration Test 再使用真实模型与真实知识库
```

---

## Exception Layer

当前应区分：

- Ingredient Exception
- LLM Exception
- Agent Exception
- Tool Exception
- RAG / Retrieval / VectorStore 相关异常

异常应保留原始原因，便于定位真实失败层。

---

## Logging Layer

Agent 日志：

```text
Request received
LLM decision
Tool selected
Tool executing
Tool completed
Observation appended
Final response generated
```

RAG 日志关注：

```text
Knowledge indexing started
Documents / chunks count
Retrieval started
Retrieved result count
Top source / score
Vector store saved / loaded
```

不应在日志中打印完整 384 维 Vector。

# 当前设计原则

1. Agent 不直接访问 Repository 或 VectorStore
2. Tool 不重复实现 Service / Retriever
3. LLMClient 只负责模型通信
4. Registry 管理工具
5. Executor 独立执行工具
6. Business Tool 与 RAG Tool 并存
7. Retriever 不重新实现 Embedding / Similarity
8. Indexer 不重新实现 Loader / Chunker / Embedding
9. Memory 与 Agent 决策分离
10. Router 不写业务逻辑
11. Unit Test 使用 Fake 隔离真实模型
12. 新能力必须做 Regression Testing
13. DeepSeek 可替换
14. 各层职责清晰

# 建议 Phase 6 架构扩展

> 基于当前 Roadmap 尚未完成的 Workflow / Planning 能力。

```text
BeautyAgent
    |
    +-- Memory
    |
    +-- Planner
    |
    +-- Workflow / Step State
    |
    +-- Tool System
    |      ├── Business Tools
    |      └── RAG Tool
    |
    +-- Result Validation / Reflection
```

Phase 6 的具体架构在进入该阶段后再正式确定。
