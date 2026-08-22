# Beauty-AI

Beauty-AI 是一个面向化妆品与护肤领域的 AI Agent 项目，用于分析：

- 化妆品成分与作用
- 肤质适用性与使用风险
- 产品和护肤知识问题
- 需要拆解为多个步骤的复杂护肤目标

项目使用 Python、FastAPI、Pydantic、LLM、Tool Calling 和本地 RAG。当前代码同时包含可直接使用的基础能力、组件级完成的规划工作流，以及尚未接通的恢复链路。

> [ARCHITECTURE.md](./ARCHITECTURE.md) 是当前唯一架构事实来源。docs 目录中的 `*PHASE5_COMPLETE.md` 是历史阶段快照，不代表当前代码状态。

## 状态说明

- ✅ **已实现组件**：代码已存在，并有与当前接口匹配的测试覆盖或可用 API 装配。
- 🟡 **组件级完成**：核心组件和成功路径已实现，但尚未形成完整、可用的生产入口。
- 🔴 **生产链路未完成**：正式 API 依赖装配或失败恢复路径仍不可运行。

## 当前项目状态

| 能力 | 状态 | 当前情况 |
|---|---|---|
| Ingredient Model / Repository / Service | ✅ 已实现组件 | 从 `data/ingredients.json` 加载并查询成分数据 |
| FastAPI 基础接口 | ✅ 已实现组件 | 提供健康检查、成分查询和旧版 AIService 接口 |
| BeautyAgent | ✅ 已实现组件 | 支持 LLM 对话、Tool Calling、Observation 和多工具循环 |
| Business Tools | ✅ 已实现组件 | `search_ingredient`、`check_skin_risk` |
| RAG 在线检索 | ✅ 已实现组件 | `search_knowledge` 可返回知识上下文和来源 |
| Planner / Plan / PlanStep | 🟡 组件级完成 | 可把 LLM JSON 转换为 1–8 步执行计划 |
| PlanExecutor / AgentStepExecutor | 🟡 组件级完成 | 可顺序执行步骤并写入 `PlanStep.result` |
| FinalAnswer / Validator | 🟡 组件级完成 | 可综合步骤结果并生成 `ValidationResult` |
| WorkflowRunner 成功路径 | 🟡 组件级完成 | Validation 首次通过时可返回 `WorkflowResult` |
| Planning Gate API | 🔴 生产链路未完成 | `get_gate()` 未向 `WorkflowRunner` 注入必需的 `recovery_manager` |
| Recovery / Reflection / Replanner | 🔴 生产链路未完成 | 缺少真实 Reflection；Replanner 为占位实现；恢复组件接口尚未统一 |
| Session Memory | 🟡 组件级完成 | 仅 Agent 实例内有效；FastAPI 每次依赖创建新实例，不能跨请求持久化 |

## 当前真实入口

### 成分查询

```http
GET /ingredients/{name}
```

真实数据流：

```text
FastAPI Route
  → IngredientService
  → IngredientRepository
  → data/ingredients.json
```

### Direct Agent

```http
POST /agent/chat/
Content-Type: application/json

{
  "session_id": "session-001",
  "message": "烟酰胺有什么作用？"
}
```

该入口绕过 Planning Gate，直接调用 BeautyAgent。Agent 可选择业务工具、RAG 工具、多个工具，或不调用工具直接回答。

### Planning Gate

```http
POST /plangate/choice/
Content-Type: application/json

{
  "session_id": "session-001",
  "message": "我是敏感肌，请分析视黄醇刺痛原因并制定四周调整方案。"
}
```

设计上，Planning Gate 应把 SIMPLE 请求路由到 BeautyAgent，把 COMPLEX 请求路由到 WorkflowRunner。

当前该 API 为 **🔴 生产链路未完成**：FastAPI 解析 `get_gate()` 依赖时，会因为 `WorkflowRunner` 缺少 `recovery_manager` 参数而失败，因此 SIMPLE 和 COMPLEX 分支都无法从该 API 到达。

### 旧版 AIService 接口

```http
POST /analyze/
POST /analyze/suitable_type
```

这些接口直接使用 AIService，不经过 BeautyAgent、Planning Gate 或 WorkflowRunner。它们属于并存的旧版调用路径，不是当前 Agent 架构的统一入口。

## Agent 与工具

BeautyAgent 当前注册三个工具：

| Tool | 输入 | 返回 |
|---|---|---|
| `search_ingredient` | `name` | Ingredient 对象或空结果 |
| `check_skin_risk` | `skin_type` | 肤质和刺激风险字典 |
| `search_knowledge` | `query` | `query`、知识 `context`、`sources` |

Agent Loop：

```text
用户/步骤提示
  → LLM
  → 可选 tool_calls
  → ToolExecutor
  → ToolRegistry
  → Tool Observation 写回 messages
  → 再次调用 LLM
  → 无 tool_calls 时返回答案
```

## RAG

当前 RAG 包含两部分：

### 离线索引组件

```text
Markdown Documents
  → DocumentLoader
  → TextChunker
  → EmbeddingService
  → KnowledgeIndexer
  → Local VectorStore JSON
```

### 在线检索组件

```text
Query
  → EmbeddingService
  → Retriever
  → VectorStore + Cosine Similarity
  → Top K SearchResult
  → RAGTool context + sources
```

本地 VectorStore 是学习和 MVP 实现，不是生产级向量数据库。

## Planning 与 Workflow

当前组件级成功路径为：

```text
PlanningGate(COMPLEX)
  → WorkflowRunner
  → Planner
  → Plan
  → PlanExecutor
  → AgentStepExecutor
  → BeautyAgent
  → Tool / RAG
  → PlanStep.result
  → FinalAnswer
  → Validator
  → ValidationResult(success=True)
  → WorkflowResult
```

该流程目前只能视为 **🟡 组件级完成**。正式 Planning Gate API 尚未完成依赖装配；Validation 失败后的 Recovery 路径也不可运行。

完整的模块职责、输入输出和已知断点见 [ARCHITECTURE.md](./ARCHITECTURE.md)。

## 项目结构

```text
Beauty-AI/
├── data/
│   ├── ingredients.json
│   ├── vector_store.json
│   └── Knowledge/
├── docs/                         # Phase 5 历史快照
├── src/
│   ├── api/                      # FastAPI routes、schemas、DI
│   ├── ai/                       # LLMClient、AIService
│   ├── agent/
│   │   ├── planning/             # Gate、Planner、PlanExecutor、AgentStepExecutor
│   │   ├── workflow/             # WorkflowRunner、FinalAnswer、WorkflowResult
│   │   ├── validation/           # Validator、ValidationResult
│   │   ├── recovery/             # 未完成的恢复链路
│   │   ├── agent.py              # BeautyAgent
│   │   ├── executor.py           # ToolExecutor
│   │   ├── registry.py           # ToolRegistry
│   │   ├── tools.py              # Business Tools
│   │   └── rag_tool.py           # RAG Tool
│   ├── rag/                      # Loader、Chunker、Embedding、VectorStore、Retriever
│   ├── services/                 # Repository / Service
│   ├── models/
│   ├── exceptions/
│   ├── config/
│   └── utils/
├── tests/
├── ARCHITECTURE.md               # 当前唯一架构事实来源
├── requirements.txt
├── pyproject.toml
└── README.md
```

`src/main.py` 目前是使用旧接口的实验脚本，不是 FastAPI 正式入口。正式服务入口是 `src.api.main:app`。

## 环境要求

- 项目目标环境：Python 3.13
- FastAPI
- Pydantic
- OpenAI Python SDK（用于访问 DeepSeek 兼容接口）
- sentence-transformers
- pytest

安装依赖：

```bash
pip install -r requirements.txt
```

环境变量：

```env
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_MODEL=deepseek-chat
APP_ENV=development
```

首次创建 `EmbeddingService` 时，sentence-transformers 可能需要加载或下载模型。

## 启动服务

```bash
python -m uvicorn src.api.main:app --reload
```

服务地址：

```text
http://127.0.0.1:8000
```

Swagger：

```text
http://127.0.0.1:8000/docs
```

## 测试状态

现有测试覆盖成分数据层、基础 API、BeautyAgent、业务 Tool、RAG 在线检索、Planner、Validator 和部分 Workflow 行为。

当前部分 Phase 6 测试仍使用旧版 `PlanExecutor`、`AgentStepExecutor` 或 `WorkflowRunner` 接口，因此不能把整个测试目录视为当前架构已全量验证。Recovery 相关测试描述了目标契约，但当前生产代码尚未满足该契约。

运行测试时应按改动范围选择相关文件，例如：

```bash
pytest tests/test_agent.py
pytest tests/test_vectorstore.py
pytest tests/test_planner.py
```

## 当前仍未完成

- Planning Gate 的生产依赖装配
- 可运行的 Reflection 实现
- 可运行的 Replanner 实现
- RecoveryManager 与 RecoveryWorkflow 的统一执行契约
- Recovery 后重新验证并稳定返回 WorkflowResult
- 跨 HTTP 请求的持久化 Session Memory
- User Profile / Long-term Memory
- 生产级 Vector Database
- 大规模、高质量专业知识库
- Docker 和生产部署方案
