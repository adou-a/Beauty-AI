# Development Log

# Phase 1：Python Engineering

状态：**✅ 完成**

完成：

- Python 基础
- Ingredient Model
- Repository Pattern
- Service Layer
- Type Hint
- Exception Handling
- Logging
- Settings
- pytest

阶段结果：

```text
Service → Repository → Knowledge Data
```

---

# Phase 2：FastAPI Backend

状态：**✅ 完成**

完成：

- HTTP / REST
- GET / POST
- Pydantic Schema
- Router
- Dependency Injection
- HTTP Exception
- API Testing
- Swagger

阶段结果：

```text
Client → FastAPI → Router → Service → Repository
```

---

# Phase 3：LLM Engineering

状态：**✅ 完成**

默认模型：**DeepSeek**

## Day 1

- LLMClient
- AIService
- LLM 架构理解

## Day 2

- DeepSeek API
- API Key
- .env
- 模型配置

## Day 3

- AIService
- Prompt Engineering

## Day 4

- 本地知识 + LLM
- IngredientService 数据注入

## Day 5

- Structured Output
- Pydantic AI Response

## Day 6

- LLM Exception
- LLM Logging
- Config

## Day 7

- FastAPI AI 接口
- 完整 LLM 调用链

阶段结果：

```text
FastAPI → AIService → LLMClient → DeepSeek → Structured Output
```

---

# Phase 4：AI Agent Core

状态：**✅ 完成**

## Day 1：Agent Concept

- LLM 与 Agent 区别
- Goal / Reasoning / Action / Observation
- BeautyAgent 骨架

## Day 2：Agent Loop

- Think → Act → Observe
- while Loop
- Tool 初始结构
- .venv

## Day 3：Tool System

- Tool Layer
- Tool 与 Service 区别
- Tool Registry
- Agent → Tool → Service → Repository

## Day 4：Tool Calling

- Tool Schema
- DeepSeek tools 参数
- Function Calling
- LLM 自主选择工具
- Tool Executor

## Day 5：Multi Tool

- search_ingredient
- check_skin_risk
- Multi Tool
- messages
- Observation

## Day 6：Agent MVP

- Agent Loop 整合
- Registry
- Executor
- Tool
- Service
- Repository
- DeepSeek Tool Calling

## Day 7：Agent Testing

- FakeLLM
- Tool Calling 行为测试
- 无需真实模型的稳定测试

## Day 8：FastAPI Agent

- FastAPI → BeautyAgent
- Agent Dependency Injection
- Agent API

## Day 9：Memory

- Short-term Memory
- Conversation Context
- Session Context
- Memory 职责分离

## Day 10：Engineering

- Agent Exception
- Agent Logging
- FakeLLM 测试完善
- Agent 模块职责整理

## Phase 4 最终结果

```text
User
 ↓
FastAPI
 ↓
BeautyAgent
 ↓
Memory
 ↓
DeepSeek
 ↓
Tool Calling
 ↓
Tool Executor
 ↓
Tool Registry
 ↓
Tools
 ↓
Service
 ↓
Repository
 ↓
Knowledge Data
 ↓
Observation
 ↓
DeepSeek
 ↓
Final Answer
```

阶段定位：

```text
Agent Core MVP
```

---

# Phase 5：RAG + Knowledge Base

状态：**✅ 完成**

目标：

让 Beauty-Agent 从：

```text
Agent + Tools + Memory
```

升级为：

```text
Agent + Tools + Memory + RAG
```

---

## Day 1：RAG Concept + Document + Chunking

完成：

- RAG 基础原理
- Retrieval-Augmented Generation
- RAG 与 Training / Fine-tuning 区别
- 结构化数据查询与非结构化知识检索区别
- `data/knowledge/*.md`
- Document Model
- Chunk Model
- DocumentLoader
- TextChunker
- chunk_size
- overlap
- source 保留
- 滑动窗口 Chunking

阶段结果：

```text
Markdown
 ↓
DocumentLoader
 ↓
Document
 ↓
TextChunker
 ↓
Chunk
```

---

## Day 2：Embedding

完成：

- Embedding 原理
- Text → Vector
- Embedding 与 LLM 职责区别
- Vector 表示
- EmbeddedChunk
- EmbeddingService
- Chunk Embedding
- Query 与 Knowledge 必须使用兼容的 Embedding 表示空间
- 固定维度 Vector 理解

阶段结果：

```text
Chunk
 ↓
EmbeddingService
 ↓
EmbeddedChunk
```

核心理解：

```text
Vector 负责语义比较
Content 负责真正提供给 LLM 阅读
```

---

## Day 3：VectorStore + Persistence + KnowledgeIndexer

完成：

- Local VectorStore
- EmbeddedChunk 存储
- add / add_many
- count / clear
- save / load
- JSON Persistence
- KnowledgeIndexer
- Offline Indexing 概念
- Query 与 Indexing 分离

阶段结果：

```text
Knowledge Documents
 ↓
Loader
 ↓
Chunker
 ↓
Embedding
 ↓
VectorStore
 ↓
Persistence
```

关键理解：

```text
知识库 Chunk 不应该每次 Query 都重新 Embedding
```

---

## Day 4：Similarity Search

完成：

- Cosine Similarity
- dot product
- vector norm
- 向量维度检查
- SearchResult
- Similarity Score
- VectorStore.search()
- Score Ranking
- Top K Retrieval
- 多 Query 检索质量测试

阶段结果：

```text
User Question
 ↓
Query Embedding
 ↓
Query Vector
 ↓
VectorStore
 ↓
Cosine Similarity
 ↓
Top K Relevant Chunks
```

核心理解：

```text
Top K = 返回数量
Score = 相似程度
```

---

## Day 5：Retriever

完成：

- Retriever 抽象层
- Query → Embedding → Vector Search 封装
- top_k 配置
- Query Validation
- VectorStore 与 Retriever 职责分离
- VectorStore 初始化 / load 时机理解
- 多 Query Retriever 测试

阶段结果：

```text
Natural Language Query
 ↓
Retriever
 ↓
Embedding
 ↓
Vector Search
 ↓
SearchResult
```

关键理解：

```text
VectorStore 面向 Vector
Retriever 面向自然语言检索
```

---

## Day 6：Context Injection + RAG Pipeline

完成：

- Context 概念
- Context Injection
- build_context()
- Source 保留
- SearchResult → LLM Context
- RAGService
- Retriever + LLMClient
- 独立 RAG Pipeline
- 使用测试知识验证模型确实读取检索结果

阶段结果：

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
RAG Answer
```

核心理解：

```text
RAG = Retrieval + Context Injection + Generation
```

---

## Day 7：RAG Tool + Agent Integration

完成：

- RAGTool
- search_knowledge
- search_knowledge Tool Schema
- Retriever 注入 RAG Tool
- Tool Registry 注册 RAG Tool
- BeautyAgent 获得知识检索能力
- Business Tool 与 RAG Tool 并存
- Agent 自主决定是否调用 RAG
- Agent + RAG Multi Tool 场景

Agent 场景采用：

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
Observation
 ↓
BeautyAgent
 ↓
DeepSeek
 ↓
Final Answer
```

而不是在 RAG Tool 内再次调用完整 RAGService 生成最终 Answer。

阶段结果：

```text
Agent + Tools + Memory + RAG
```

---

## Day 8：RAG Testing + Engineering Review

完成：

- Similarity Unit Test
- VectorStore Test
- Retriever Test
- RAG Tool Test
- Agent + RAG Behavior Test
- FakeEmbeddingService
- FakeLLM 延续到 RAG Agent
- Regression Testing
- Unit Test 与 Integration Test 区别
- RAG Logging 检查
- RAG Exception 基础
- Top K 与真实相关性区别
- Similarity Threshold 概念
- Offline / Online Pipeline 总复盘
- Phase 5 架构总验收

测试原则：

```text
Unit Test
→ Fake / 固定输入输出

Integration Test
→ 真实 Embedding + 真实 Knowledge + 真实 DeepSeek
```

Regression Testing 目标：

```text
新增 RAG 后
原有 Agent / Business Tool 仍然正常
```

---

# Phase 5 最终结果

## Offline / Indexing

```text
Knowledge Documents
 ↓
DocumentLoader
 ↓
TextChunker
 ↓
EmbeddingService
 ↓
VectorStore
 ↓
Persistence
```

## Online / Retrieval

```text
User Query
 ↓
Retriever
 ↓
Query Embedding
 ↓
Similarity Search
 ↓
Top K SearchResult
```

## Agent + RAG

```text
User
 ↓
FastAPI
 ↓
BeautyAgent
 ↓
Memory
 ↓
DeepSeek
 ↓
Tool Decision
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
                           VectorStore
                                │
                                v
                         Knowledge Base
│                               │
└────────── Observation ─────────┘
                ↓
            BeautyAgent
                ↓
             DeepSeek
                ↓
          Final Answer
```

当前 Beauty-AI 定位：

```text
垂直领域 AI Agent + RAG MVP
```

---

# 当前完成阶段

- Phase 1：Python Engineering —— ✅
- Phase 2：FastAPI Backend —— ✅
- Phase 3：LLM Engineering —— ✅
- Phase 4：AI Agent Core —— ✅
- Phase 5：RAG + Knowledge Base —— ✅

# 当前未完成能力

- Persistent / Long-term Memory
- User Profile
- Workflow
- Planning
- Reflection / Validation
- Production Vector Database
- 真实 Knowledge Base 深度建设
- Docker / Production Deployment
- 完整前端

# 建议下一阶段

## Phase 6：Workflow + Planning

> 基于现有 Roadmap 中尚未完成的 Workflow / Planning / Reflection 能力进行下一阶段规划。

阶段目标：

```text
Agent 能调用工具
+
Agent 能检索知识

        ↓

Agent 能处理复杂目标
+
拆解任务
+
规划多步骤执行
+
维护执行状态
+
验证结果
```

具体 Day 计划进入 Phase 6 时再确定。
