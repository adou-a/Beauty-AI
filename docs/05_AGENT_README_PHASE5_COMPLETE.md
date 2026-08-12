# Beauty-Agent README

# Agent 简介

Beauty-Agent 是 Beauty-AI 的核心 AI Agent。

Phase 4 完成了：

```text
AI Agent Core
```

Phase 5 在此基础上增加了：

```text
RAG + Knowledge Base
```

Beauty-Agent 现在不是让 DeepSeek 直接回答所有问题，而是让模型根据用户目标自主决定：

```text
直接回答

或

调用 Business Tool

或

调用 RAG Tool

或

进行 Multi Tool 多步骤执行
```

当前核心：

```text
LLM
+
Agent Loop
+
Tools
+
Memory
+
RAG
+
Testing
```

# 当前能力

- DeepSeek Tool Calling
- Agent Loop
- Tool Schema
- Tool Registry
- Tool Executor
- Multi Tool
- Tool Result Observation
- Ingredient Service / Repository 接入
- FastAPI Agent API
- Short-term Conversation Memory
- Session Context
- FakeLLM Testing
- Agent Exception
- Agent Logging
- Document Knowledge Base
- Chunking
- Embedding
- Local VectorStore
- Vector Persistence
- Similarity Search
- Retriever
- RAG Pipeline
- Context Injection
- RAG Tool
- `search_knowledge`
- Agent + RAG
- FakeEmbedding Testing
- Regression Testing

# Agent 架构

```text
User
 ↓
FastAPI
 ↓
BeautyAgent
 ↓
Memory / Context
 ↓
LLMClient
 ↓
DeepSeek
 ↓
Tool Calling
 ↓
ToolExecutor
 ↓
ToolRegistry
 ↓
┌───────────────────────────────┐
│                               │
Business Tools               RAG Tool
│                               │
Service / Repository          Retriever
                                │
                                v
                        EmbeddingService
                                │
                                v
                           VectorStore
                                │
                                v
                         Knowledge Base
│                               │
└────────── Tool Result ─────────┘
                ↓
            BeautyAgent
                ↓
             DeepSeek
                ↓
          Final Answer
```

# Agent Loop

```text
Think
 ↓
Act
 ↓
Observe
 ↓
Think
 ↓
Answer
```

核心逻辑：

```text
while True

    调用 LLM

    如果有 tool_calls
        执行 Tool
        把 Tool Result 加入 messages
        continue

    否则
        return 最终回答
```

Phase 5 并没有替换 Agent Loop。

RAG 是 Agent 新增加的一项能力。

# Tool Calling

普通函数调用：

```text
程序提前决定调用哪个函数
```

Agent Tool Calling：

```text
用户目标
 ↓
DeepSeek 分析
 ↓
选择 Tool
 ↓
返回 tool_call
 ↓
Python 执行
```

原则：

```text
LLM 决定需要什么能力
Python 负责真正执行能力
```

# 当前 Tools

## 1. search_ingredient

用途：

查询护肤成分结构化信息。

示例 Schema：

```json
{
  "name": "search_ingredient",
  "description": "查询护肤成分信息",
  "parameters": {
    "name": "string"
  }
}
```

执行：

```text
search_ingredient
 ↓
IngredientService.find_ingredient()
 ↓
IngredientRepository
 ↓
ingredients.json
```

适合：

```text
明确成分名称
明确结构化数据查询
```

---

## 2. check_skin_risk

用途：

根据肤质提供基础风险提示。

示例参数：

```json
{
  "skin_type": "string"
}
```

适合：

```text
基础肤质风险判断
```

---

## 3. search_knowledge

用途：

从护肤专业知识库检索与用户问题相关的非结构化资料。

示例参数：

```json
{
  "query": "string"
}
```

执行：

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
Relevant Chunks
 ↓
Context
```

适合：

```text
护肤原理
成分使用方法
复杂成分风险
肤质护理
皮肤屏障
需要从长文知识中检索的信息
```

# Business Tool 与 RAG Tool

Business Tool：

```text
Agent 的业务能力接口
```

例如：

```text
search_ingredient
 ↓
Service
 ↓
Repository
```

RAG Tool：

```text
Agent 的知识检索能力接口
```

例如：

```text
search_knowledge
 ↓
Retriever
 ↓
VectorStore
 ↓
Knowledge Base
```

二者不是替代关系。

复杂 Query 可以同时使用多种能力。

# RAG 是什么

RAG：

```text
Retrieval-Augmented Generation
```

核心：

```text
Retrieval
+
Context Injection
+
Generation
```

RAG 不是：

```text
重新训练 DeepSeek
```

而是：

```text
用户问题
↓
检索当前需要的少量知识
↓
把知识放入本次上下文
↓
DeepSeek 根据资料回答
```

# RAG Offline / Indexing

知识库建立流程：

```text
Knowledge Markdown
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
Persistence
```

Indexing 不应该每次用户 Query 都重新完整执行。

知识库更新后，需要重新建立或更新对应 Index。

# RAG Online / Query

```text
User Query
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
Top K SearchResult
```

然后：

```text
SearchResult
 ↓
Context
 ↓
Agent Observation / RAGService
```

# Chunking

Chunk 的目的：

```text
把长文档切成适合检索的知识单元
```

核心参数：

```text
chunk_size
overlap
```

Overlap 用于降低重要语义刚好被边界切开的风险。

Chunk 保留：

- content
- source
- index

# Embedding

Embedding：

```text
Text
↓
Vector
```

目的：

让计算机可以对文本语义进行数学比较。

核心理解：

```text
Vector 负责找知识
Content 负责给 LLM 看
```

知识库 Chunk 与 Query 应使用兼容的 Embedding 表示空间。

# VectorStore

当前实现：

```text
Local VectorStore + JSON Persistence
```

保存：

- content
- source
- index
- vector

支持：

- add
- add_many
- save
- load
- count
- clear
- similarity search
- top_k

说明：

当前实现主要用于学习底层机制与完成 MVP，不代表最终生产级 Vector Database。

# Similarity Search

当前核心算法：

```text
Cosine Similarity
```

```text
Query Vector
↕
Chunk Vector
↓
Similarity Score
```

随后：

```text
排序
↓
Top K
```

必须区分：

```text
Top K
=
返回排名最高的 K 个结果
```

与：

```text
Similarity Threshold
=
判断结果是否足够相关
```

Top K 本身不能保证返回结果真的相关。

# Retriever

Retriever 输入：

```text
Natural Language Query
```

Retriever 输出：

```text
list[SearchResult]
```

内部：

```text
Query
↓
Embedding
↓
Vector Search
↓
Relevant Knowledge
```

原则：

```text
Retriever 负责协调检索
不重新实现 Embedding / Similarity / Storage
```

# Context Injection

Retriever 找到知识以后，需要转换成 LLM 可以阅读的 Context。

示例：

```text
[资料1]
来源：retinol.md

视黄醇初期使用可能出现……

[资料2]
来源：sensitive_skin.md

敏感肤质……
```

Context Injection：

```text
Relevant Context
+
User Question
↓
LLM
```

它不等于训练模型。

# RAGService

独立 RAG Pipeline：

```text
Question
 ↓
Retriever
 ↓
Relevant Chunks
 ↓
Context
 ↓
LLMClient
 ↓
DeepSeek
 ↓
Answer
```

用途：

验证完整 RAG Pipeline 可以独立运行。

# RAGTool

Agent 集成后：

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
Context
 ↓
Tool Observation
 ↓
BeautyAgent
 ↓
DeepSeek
 ↓
Final Answer
```

RAG Tool 不再次调用完整 `RAGService.ask()` 生成最终答案。

原因：

避免：

```text
Agent LLM
↓
RAG LLM
↓
Agent LLM
```

产生重复生成链路。

# Tool Schema

位置：

```text
src/agent/schemas.py
```

作用：

告诉 DeepSeek：

- Tool 名称
- Tool 描述
- 参数
- 参数类型
- required

当前主要 Tools：

```text
search_ingredient
check_skin_risk
search_knowledge
```

Schema 不执行代码。

当 Tool 数量增加后，Description 更重要，因为 DeepSeek 需要根据描述判断不同 Tool 的职责边界。

# Tool Registry

位置：

```text
src/agent/registry.py
```

职责：

```text
register
get
get_tools
exists
```

价值：

增加 `search_knowledge` 后，不需要把 RAG 逻辑写死在 Agent Loop 内。

# Tool Executor

位置：

```text
src/agent/executor.py
```

流程：

```text
tool_call.function.name
 ↓
tool_call.function.arguments
 ↓
registry.get()
 ↓
tool(**arguments)
 ↓
Tool Result
```

原则：

```text
Agent 决定做什么
Executor 负责执行
```

# Tool 与 Service / Retriever

Service：

```text
系统业务逻辑
```

Retriever：

```text
知识检索逻辑
```

Tool：

```text
暴露给 Agent 的能力接口
```

正确：

```text
Agent → Business Tool → Service → Repository
```

以及：

```text
Agent → RAG Tool → Retriever → VectorStore
```

# Memory

当前：

```text
Short-term Conversation Memory
+
Session Context
```

用途：

让同一 Session 理解前文。

未来：

- Persistent Memory
- User Profile
- Long-term Memory

RAG 与 Memory 不同：

```text
Memory
=
对话 / 用户上下文

RAG
=
外部知识检索
```

# FastAPI Agent API

关系：

```text
FastAPI → BeautyAgent
```

FastAPI：

- HTTP
- Validation
- Response
- DI

BeautyAgent：

- Agent Loop
- Tool Calling
- Memory
- RAG Tool Decision
- Execution

# Dependency Injection

当前 Agent 系统依赖大致为：

```text
IngredientRepository
 ↓
IngredientService
 ↓
Business Tools

EmbeddingService
 ↓
VectorStore.load()
 ↓
Retriever
 ↓
RAGTool

Business Tools + RAGTool
 ↓
ToolRegistry
 ↓
ToolExecutor

LLMClient
Memory
Tool Schemas
 ↓
BeautyAgent
```

测试时可以替换：

```text
Real LLM
↓
FakeLLM
```

以及：

```text
Real Embedding
↓
FakeEmbeddingService
```

# Testing

## FakeLLM Testing

Agent 行为测试重点：

- 是否调用 Tool
- 是否选择正确 Tool
- 参数是否合理
- Observation 是否加入 messages
- 是否继续 Loop
- 无 Tool 时是否直接返回
- 错误 Tool 是否正确抛异常
- RAG Tool 是否可以加入 Multi Tool 流程

## FakeEmbeddingService

解决：

```text
Unit Test 不依赖真实 Embedding Model
```

使用固定输入输出测试：

- VectorStore
- Retriever
- Similarity Search

## Regression Testing

目标：

```text
加入 RAG 后
旧 Agent / Business Tool 能力仍正常
```

## Unit Test 与 Integration Test

```text
Unit Test
→ Fake / Fixed Vector / Stable
```

```text
Integration Test
→ Real Embedding + Real Knowledge + Real DeepSeek
```

# Agent Exception

当前需要继续区分：

```text
AgentError
ToolNotFoundError
ToolExecutionError
LLMError
MemoryError
RAG / Retrieval / VectorStore Error
```

原则：

异常层次应该帮助判断真正失败的是：

```text
Agent
Tool
LLM
Embedding
Retriever
VectorStore
```

而不是全部变成一个模糊错误。

# Agent / RAG Logging

Agent：

```text
Agent received request
LLM decision received
Selected tool
Executing tool
Tool completed
Observation appended
Final response generated
```

RAG：

```text
Knowledge indexing started
Documents / chunks count
Retrieval started
Retrieved knowledge count
Top source / similarity score
Vector store saved / loaded
```

不建议记录：

```text
完整高维 Vector
```

因为日志价值低、体积大、可读性差。

# 示例 1：结构化成分查询

用户：

```text
查询烟酰胺的信息
```

目标过程：

```text
BeautyAgent
 ↓
DeepSeek
 ↓
search_ingredient("烟酰胺")
 ↓
Observation
 ↓
DeepSeek
 ↓
Final Answer
```

# 示例 2：知识库查询

用户：

```text
为什么皮肤屏障受损以后容易刺痛？
```

目标过程：

```text
BeautyAgent
 ↓
DeepSeek
 ↓
search_knowledge(...)
 ↓
Retriever
 ↓
Relevant Knowledge
 ↓
Observation
 ↓
DeepSeek
 ↓
Final Answer
```

# 示例 3：Multi Tool + RAG

用户：

```text
我是敏感肌，使用视黄醇以后脱皮刺痛，需要注意什么？
```

可能过程：

```text
BeautyAgent
 ↓
DeepSeek
 ↓
search_ingredient("视黄醇")
 ↓
Observation
 ↓
check_skin_risk("敏感肌")
 ↓
Observation
 ↓
search_knowledge(
  "敏感肌使用视黄醇脱皮刺痛的原因和注意事项"
)
 ↓
Retriever
 ↓
Observation
 ↓
DeepSeek
 ↓
Final Answer
```

具体 Tool 顺序由 DeepSeek 根据用户目标决定，不要求永远固定。

# 当前状态

Phase 4：**✅ AI Agent Core 完成**

Phase 5：**✅ RAG + Knowledge Base 完成**

当前定位：

```text
垂直领域 AI Agent + RAG MVP
```

# 尚未完成

- Persistent / Long-term Memory
- User Profile
- Workflow
- Planning
- Reflection / Validation
- Production-grade Vector Database
- 更完整的真实专业 Knowledge Base
- Docker / Production Deployment
- 完整前端

# 建议下一阶段

## Phase 6：Workflow + Planning

> 基于当前 Roadmap 尚未完成的 Workflow / Planning / Reflection 能力。

目标：

让 Agent 从：

```text
自主选 Tool
+
自主检索 Knowledge
```

继续升级为：

```text
复杂任务拆解
+
多步骤计划
+
Workflow 状态管理
+
执行结果验证
```

具体 Day 计划进入 Phase 6 时再正式设计。
