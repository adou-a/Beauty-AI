# Beauty-AI Project Context

## 项目定位

Beauty-AI 是 **AI Agent Developer Roadmap** 的主实践项目。

项目目标不是做一个简单护肤问答机器人，而是通过 Beauty-AI 完整学习并实现 AI Agent 的核心工程能力，最终把能力迁移到其他领域 Mini Agent。

## 最终目标

- 完成一个可展示、可测试、可部署的垂直领域 AI Agent
- 掌握从 0 构建 Agent 的核心工程能力
- 理解 Agent 底层机制，而不是只会调用框架
- 将能力迁移到其他领域 Mini Agent
- 形成可用于作品集、求职和产品化展示的完整项目

## 核心方向

- 护肤成分知识库
- Python Engineering
- FastAPI Backend
- LLM Engineering
- DeepSeek
- Prompt Engineering
- Structured Output
- Tool Calling
- Multi Tool
- Agent Loop
- Tool Registry
- Tool Executor
- Conversation Memory
- FakeLLM Testing
- RAG
- Document Knowledge Base
- Embedding
- Vector Search
- Retriever
- Agent + RAG
- Workflow / Planning
- API 产品化
- Deployment

## 当前学习原则

- 项目实践优先
- 每阶段明确目标和验收标准
- 每天明确代码任务
- 理解底层原理
- 不盲目堆框架
- 先自己实现核心机制，再学习框架封装
- 每天任务量需要足够
- 必须能解释为什么这样设计
- 新功能不能破坏已有功能，需要 Regression Testing
- Unit Test 优先隔离真实 LLM / Embedding 等不稳定外部依赖

# 已完成阶段

## Phase 1：Python Engineering

状态：**✅ 完成**

完成：

- Ingredient Model
- Repository Pattern
- Service Layer
- Type Hint
- Exception Handling
- Logging
- Settings
- pytest
- 模块化工程结构

阶段结果：

```text
Service → Repository → Knowledge Data
```

---

## Phase 2：FastAPI Backend

状态：**✅ 完成**

完成：

- HTTP / REST
- GET / POST
- Router
- Pydantic Schema
- Dependency Injection
- HTTP Exception
- Swagger
- API Testing

阶段结果：

```text
Client → FastAPI → Router → Service → Repository
```

---

## Phase 3：LLM Engineering

状态：**✅ 完成**

默认大模型：**DeepSeek**

完成：

- LLMClient
- AIService
- DeepSeek API
- API Key / .env
- Prompt Engineering
- 本地成分数据与 LLM 融合
- Structured Output
- Pydantic AI Response
- LLM Exception
- LLM Logging
- FastAPI AI 接口

阶段结果：

```text
FastAPI → AIService → LLMClient → DeepSeek → Structured Output
```

---

## Phase 4：AI Agent Core

状态：**✅ 完成**

完成：

- BeautyAgent
- Agent Loop
- Tool System
- Tool Schema
- Tool Calling
- Multi Tool
- Tool Registry
- Tool Executor
- DeepSeek 自主选择工具
- Tool Observation 回传
- FakeLLM Testing
- Agent Exception
- Agent Logging
- FastAPI Agent API
- Short-term Conversation Memory
- Session Context

阶段结果：

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
Business Tools
 ↓
Service / Repository
 ↓
Observation
 ↓
DeepSeek
 ↓
Final Answer
```

---

## Phase 5：RAG + Knowledge Base

状态：**✅ 完成**

Phase 5 的目标是让 Beauty-Agent 从“会调用业务工具”升级为“会主动检索外部专业知识”。

完成：

- RAG 原理
- Document Knowledge Base
- DocumentLoader
- TextChunker
- Chunk Size / Overlap
- Document / Chunk / EmbeddedChunk / SearchResult 数据模型
- EmbeddingService
- 文本 → Vector
- Local VectorStore
- Vector Persistence
- KnowledgeIndexer
- Offline Indexing Pipeline
- Cosine Similarity
- Similarity Search
- Top K Retrieval
- Retriever
- Context Building
- Context Injection
- RAGService / 独立 RAG Pipeline
- RAG Tool
- `search_knowledge` Tool Schema
- Agent + RAG Integration
- Business Tool 与 RAG Tool 并存
- FakeEmbeddingService Testing
- FakeLLM Agent Behavior Testing
- RAG Regression Testing
- RAG Logging / Exception 基础工程化

### Phase 5 核心认知

```text
RAG ≠ Training
RAG ≠ Fine-tuning

RAG = Retrieval + Context Injection + Generation
```

### Offline / Indexing

```text
Knowledge Documents
        ↓
DocumentLoader
        ↓
Documents
        ↓
TextChunker
        ↓
Chunks
        ↓
EmbeddingService
        ↓
Vectors
        ↓
VectorStore
        ↓
Persistence
```

### Online / Query

```text
User Question
      ↓
EmbeddingService
      ↓
Query Vector
      ↓
Retriever
      ↓
Similarity Search
      ↓
Top K Relevant Chunks
      ↓
Context
      ↓
DeepSeek
      ↓
Answer
```

### Agent + RAG

```text
User
 ↓
BeautyAgent
 ↓
DeepSeek
 ↓
Tool Decision
 ↓
┌─────────────────────────────┐
│                             │
Business Tools            RAG Tool
│                             │
↓                             ↓
Service / Repository       Retriever
                              ↓
                        VectorStore
                              ↓
                        Knowledge Base
                              ↓
                           Context
│                             │
└──────── Observation ─────────┘
              ↓
          BeautyAgent
              ↓
           DeepSeek
              ↓
        Final Answer
```

# 当前系统定位

Beauty-AI 当前已经从：

```text
Agent Core MVP
```

升级为：

```text
垂直领域 AI Agent + RAG MVP
```

当前系统已经具备：

```text
Python Engineering
+
FastAPI Backend
+
DeepSeek LLM Engineering
+
Agent Loop
+
Tool Calling / Multi Tool
+
Conversation Memory
+
RAG / Knowledge Retrieval
+
Testing
```

# 当前知识库定位

Phase 5 已经完成了 **知识库工程链路**。

当前 Local VectorStore / JSON Persistence 的主要目的，是理解并实现 Vector Store 的底层机制；它不是最终生产级 Vector Database。

真实 Beauty-AI Knowledge Base 可以从当前测试知识逐步扩展为高质量 V1 知识库，并继续补充：

- 更可靠的真实资料
- Metadata
- 来源机构
- Source URL
- 更新时间
- Category
- 知识更新与重建 Index 流程

这些扩展不影响 Phase 5 核心能力已经完成。

# 尚未完成

后续阶段仍需完成：

- Persistent / Long-term Memory
- User Profile
- Workflow
- Planning
- Reflection / Validation
- Production-grade Vector Database
- 更完整的真实专业 Knowledge Base
- Docker / Production Deployment
- 完整前端
- 产品化与部署

# 建议下一阶段

## Phase 6：Workflow + Planning

> 这是基于当前 Roadmap 尚未完成项的下一阶段规划。

目标：

让 Beauty-Agent 从：

```text
会选择工具
+
会检索知识
```

升级为：

```text
面对复杂目标
↓
拆解任务
↓
规划执行步骤
↓
调用多个能力
↓
维护执行状态
↓
验证结果
```

Phase 6 的具体 Day 任务与验收标准应在进入阶段时再正式确定。
