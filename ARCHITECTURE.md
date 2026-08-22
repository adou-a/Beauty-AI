# Beauty-AI Current Architecture

## 0. Document Authority

本文档是 Beauty-AI **当前唯一架构事实来源**，描述当前工作区代码，而不是目标架构或未来计划。

- `README.md` 面向项目介绍和使用者。
- docs 目录中的 `*PHASE5_COMPLETE.md` 是历史阶段快照。
- 当历史文档、README 与本文冲突时，以本文和实际代码为准。

### 状态标记

- ✅ **已实现组件**：代码已存在，并有与当前接口匹配的测试覆盖或可用 API 装配。
- 🟡 **组件级完成**：组件和局部成功路径已实现，但未形成完整生产链路。
- 🔴 **生产链路未完成**：正式入口、依赖装配或失败恢复路径不可运行。

## 1. Architecture Summary

Beauty-AI 当前同时存在四类请求路径，而不是单一的 Agent 入口：

```text
FastAPI
├── GET  /ingredients/{name}  → Ingredient Service Path
├── POST /analyze/*           → Legacy AIService Path
├── POST /agent/chat/         → Direct BeautyAgent Path
└── POST /plangate/choice/    → Planning Gate Path（当前装配失败）
```

当前架构状态：

| 范围 | 状态 | 结论 |
|---|---|---|
| Ingredient 数据链 | ✅ 已实现组件 | API、Service、Repository 和 JSON 数据可连接 |
| Direct BeautyAgent 链 | ✅ 已实现组件 | API 已装配 Tool、RAG 和实例内 Memory |
| Planning / Workflow 成功路径 | 🟡 组件级完成 | 组件存在，Validation 首次成功的路径可组合 |
| Planning Gate 正式入口 | 🔴 生产链路未完成 | `get_gate()` 无法构造 `WorkflowRunner` |
| Validation Failure / Recovery | 🔴 生产链路未完成 | Reflection、Replanner 和恢复执行契约未完成 |

## 2. Current API Entry Points

### 2.1 Ingredient Service Path

```text
GET /ingredients/{name}
  → ingredient_routes.get_ingredient(name)
  → IngredientService.find_ingredient(name)
  → IngredientRepository.get_all()
  → data/ingredients.json
  → Ingredient / HTTP 404 / HTTP 500
```

职责：

- API 负责 HTTP 参数、响应和异常映射。
- Service 负责查询规则。
- Repository 负责加载 JSON 并构造 Ingredient。

该路径不使用 LLM、Agent、Planning 或 RAG。

### 2.2 Legacy AIService Path

```text
POST /analyze/
  → AIService.analyze_ingrdient(name)
  → IngredientService
  → LLMClient
  → IngredientAnalysis 或未找到提示
```

`POST /analyze/suitable_type` 也直接调用 AIService。这些是旧版 AI 调用路径，不经过 BeautyAgent 或 WorkflowRunner。

### 2.3 Direct BeautyAgent Path

```text
POST /agent/chat/
  → AgentRequest(session_id, message)
  → get_agent()
  → BeautyAgent.run(session_id, message)
  → string
  → AgentResponse(answer)
```

`get_agent()` 每次构造：

```text
IngredientRepository
  → IngredientService
  → IngredientSearchTool

EmbeddingService
VectorStore.load()
  → Retriever(top_k=3)
  → RAGTool

Tool Schemas
  + ToolRegistry
  + ToolExecutor
  + LLMClient
  + new MemoryStore
  → BeautyAgent
```

该入口是当前可到达的 Agent 路径，但 MemoryStore 由依赖函数新建，因此会话仅在本次 Agent 实例内保存，不能跨 HTTP 请求持久化。

### 2.4 Planning Gate Path

设计入口：

```text
POST /plangate/choice/
  → PlangateRequest(session_id, message)
  → Depends(get_gate)
  → PlanningGate.choice(user_input, session_id)
  → PlangateResponse(answer)
```

当前真实执行在依赖装配阶段中断：

```text
get_gate()
  → 创建 Planner
  → 创建 AgentStepExecutor
  → 创建 PlanExecutor
  → 创建 FinalAnswer
  → 创建 Validator
  → WorkflowRunner(...)
  → TypeError: missing recovery_manager
```

`WorkflowRunner.__init__` 要求 `recovery_manager`，但 `get_gate()` 没有创建或注入它。因此该 API 当前是 **🔴 生产链路未完成**，请求不会到达 PlanningGate 的分类逻辑。

## 3. Planning Gate Responsibilities

PlanningGate 当前不是纯分类器，而是“分类 + 路由 + 答案解包”组件。

输入：

```text
user_input: str
session_id: str
```

内部分类输出：

```text
SIMPLE | COMPLEX
```

对外输出：

```text
str  # 最终答案
```

组件行为：

```text
PlanningGate.choice
  → LLMClient.chat(classification messages)
  → 严格解析 SIMPLE / COMPLEX
  ├── SIMPLE  → BeautyAgent.run(...) → str
  └── COMPLEX → WorkflowRunner.run(...) → WorkflowResult.final_answer
```

PlanningGate 负责选择路径并调用下游，不负责创建 Plan、执行 PlanStep 或选择具体 Tool。

## 4. Direct Agent Architecture

### 4.1 BeautyAgent

输入：

```text
session_id: str
user_input: str
```

输出：

```text
str
```

真实循环：

```text
MemoryStore.get_memory(session_id)
  → 添加 user message
  → LLMClient.chat(messages, tools)
  ├── 无 tool_calls
  │    → 添加 assistant message
  │    → 返回 response.content
  └── 有 tool_calls
       → 添加 assistant tool_calls message
       → 按返回顺序执行每个 Tool Call
       → 添加 tool observation message
       → 继续调用 LLM
```

BeautyAgent 负责：

- 保存当前实例内的对话消息。
- 调用 LLM。
- 根据 LLM 返回选择工具。
- 把工具结果写回对话。
- 在无 Tool Call 时返回回答。

BeautyAgent 不直接依赖 Repository、VectorStore、EmbeddingService 或 Cosine Similarity。

### 4.2 Tool Layer

```text
BeautyAgent
  → ToolExecutor.execute(tool_call)
  → 解析 function.name 和 JSON arguments
  → ToolRegistry.get(name)
  → tool(**arguments)
```

| Tool | 下游 | 返回 |
|---|---|---|
| `search_ingredient` | IngredientService → Repository | Ingredient 或空结果 |
| `check_skin_risk` | IngredientSearchTool 内部逻辑 | 风险字典 |
| `search_knowledge` | RAGTool → Retriever | query、context、sources 字典 |

Tool 只返回信息，不负责生成最终用户答案。

## 5. Planning and Workflow Architecture

本节描述当前组件代码可组成的成功路径。由于正式 Gate 依赖未完成，它的整体状态是 **🟡 组件级完成**。

### 5.1 Component-Level Happy Path

前提：

- 手工或测试代码正确提供 `recovery_manager`。
- Planner、Agent、FinalAnswer 和 Validator 的 LLM 调用成功。
- 所有 PlanStep 完成。
- 第一次 Validation 返回 `success=True`。

数据流：

```text
WorkflowRunner.run(user_input, session_id)
  → Planner.create_plan(user_input)
  → Plan(goal, steps)
  → ExecutorContext(session_id)
  → WorkflowState.start()
  → PlanExecutor.execute(plan, context, state)
       → 对每个 PENDING PlanStep
       → AgentStepExecutor.execute(step, context, goal)
       → BeautyAgent.run(session_id, step_prompt)
       → 可选 Tool / RAG
       → str
       → PlanStep.result = str
       → PlanStep.status = COMPLETED
  → 检查所有 PlanStep 都是 COMPLETED
  → 收集非空 PlanStep.result
  → FinalAnswer.synthesis(user_input, results)
  → Validator.validate(user_input, plan.goal, answer)
  → ValidationResult(success=True, reasons=[])
  → WorkflowState.finish()
  → WorkflowResult
```

### 5.2 Component Contracts

| Component | Input | Output | State / Side Effect |
|---|---|---|---|
| Planner | `user_input: str` | `Plan` | 无执行状态 |
| Plan | `goal`、`steps` | 领域对象 | 持有 PlanStep |
| PlanStep | id、description | 可变领域对象 | status、result 被 Executor 更新 |
| PlanExecutor | Plan、ExecutorContext、WorkflowState | 同一个 Plan | 顺序更新步骤与 current_step_id |
| AgentStepExecutor | PlanStep、ExecutorContext、goal | 非空 `str` | 构造单步 Prompt，调用 BeautyAgent |
| BeautyAgent | session_id、单步 Prompt | `str` | 可调用 Tool/RAG，更新实例内 Memory |
| FinalAnswer | user_input、`list[str]` | `str` | LLM 综合步骤结果 |
| Validator | user_input、goal、final_answer | ValidationResult | 不修改答案 |
| WorkflowRunner | user_input、session_id | 成功时 WorkflowResult | 管理 WorkflowState 和流程顺序 |

### 5.3 Responsibility Boundaries

#### Planner

负责：

- 理解目标。
- 生成结构化 `PlanOutput`。
- 转换为 `Plan` 和顺序编号的 `PlanStep`。

不负责：

- Tool 或 RAG 调用。
- 执行步骤。
- 最终答案。
- 执行状态管理。

#### PlanExecutor

负责：

- 顺序扫描 PlanStep。
- 跳过 COMPLETED 和非 PENDING 步骤。
- 设置 RUNNING / COMPLETED / FAILED。
- 把 Step Executor 返回值写入 `PlanStep.result`。

它不负责生成 Plan、选择 Tool 或综合最终回答。步骤结果列表最终由 WorkflowRunner 收集。

#### AgentStepExecutor

负责：

- 把 Plan goal 和当前步骤描述转换为单步 Prompt。
- 使用 Workflow 的 session_id 调用 BeautyAgent。
- 拒绝空字符串结果。
- 将 Agent 异常包装为 `AgentStepExecutionError`。

#### WorkflowRunner

负责：

- 调用 Planner。
- 创建 ExecutorContext 和 WorkflowState。
- 调用 PlanExecutor。
- 检查所有步骤完成。
- 收集步骤结果。
- 调用 FinalAnswer 和 Validator。
- 在验证失败时尝试进入 RecoveryManager。
- 成功路径返回 WorkflowResult。

WorkflowRunner 不直接执行 Tool，不直接修改单个 PlanStep 的执行逻辑。

## 6. Domain Models and State Ownership

### Plan

```text
goal: str
steps: list[PlanStep]
```

### PlanStep

```text
id: int
description: str
status: PENDING | RUNNING | COMPLETED | FAILED
result: str | None
```

状态生命周期：

```text
PENDING → RUNNING → COMPLETED
                  ↘ FAILED
```

### WorkflowState

```text
status: PENDING | RUNNING | COMPLETED | FAILED
current_step_id: int | None
error: str | None
```

WorkflowState 当前只存在于一次 `WorkflowRunner.run()` 调用中，不持久化，也不通过 API 返回。

### WorkflowResult

```text
user_input: str
goal: str
step_results: list[str]
final_answer: str
validation: ValidationResult
```

### ValidationResult

```text
success: bool
reasons: list[str]
```

## 7. Final Answer and Validation

### FinalAnswer

FinalAnswer 使用 LLM 把 `PlanStep.result` 列表综合为面向用户的字符串。它不执行 Tool，也不重新规划。

### Validator

输入：

```text
user_input
goal
final_answer
```

输出：

```text
ValidationResult(success, reasons)
```

当前规则：

- LLM 输出必须是合法 JSON。
- `ValidationOutput` 启用 strict 和 `extra="forbid"`。
- `success=True` 时，reasons 必须为空列表。
- Validator 判断目标完成度和回答完整性。
- Validator 不检查事实正确性，不修改答案，不负责 Recovery。

## 8. Recovery / Reflection Status

Recovery 相关代码目前是 **🔴 生产链路未完成**，不能描述为已实现能力。

已存在的数据模型或骨架：

- `RecoveryContext`
- `ReflectionResult`
- `RecoveryResult`
- `ReplanResult`
- `RecoveryExecutionContext`
- `RecoveryManager`
- `RecoveryWorkflow`
- `Replanner` 类骨架

当前断点：

1. 没有生产可用的 Reflection 实现；Reflection 只在测试中以 Fake 对象出现。
2. `Replanner.replan()` 仍是占位实现，不会生成真实 ReplanResult。
3. RecoveryManager 的 replan 分支没有从 `ReplanResult.new_plan` 提取 Plan。
4. RecoveryManager 创建 RecoveryExecutionContext 时使用了错误的关键字 `user_input`；模型字段是 `use_input`。
5. RecoveryManager 把 `action` 设置为 `None`，与声明的字符串契约不一致。
6. RecoveryWorkflow 依赖 `executor.executor(plan)` 和 `final_answer.generate(...)`，与生产 PlanExecutor/FinalAnswer 接口不一致。
7. WorkflowRunner 使用 `recovery_result == True` 判断 dataclass 结果，不能正确读取 `RecoveryResult.recovered`。
8. Validation 失败分支可能返回字符串，而方法声明和 PlanningGate 都期待 WorkflowResult。
9. `get_gate()` 没有任何 RecoveryManager 装配。

因此当前没有可声明的真实 Recovery 数据流。以下只表示目标方向，不表示完成：

```text
ValidationResult(success=False)
  → RecoveryContext
  → Reflection
  → optional Replan
  → Recovery Workflow
  → recovered answer
  → second validation
  → WorkflowResult
```

## 9. RAG Architecture

### 9.1 Offline Indexing Components

```text
Knowledge Markdown Files
  → DocumentLoader
  → Document
  → TextChunker
  → Chunk
  → EmbeddingService
  → EmbeddedChunk
  → KnowledgeIndexer
  → VectorStore.save()
  → data/vector_store.json
```

### 9.2 Online Retrieval

```text
query
  → EmbeddingService.embed_text(query)
  → query_vector
  → VectorStore.search(query_vector, top_k)
  → cosine_similarity
  → list[SearchResult]
  → build_context(results)
```

### 9.3 Agent RAG Tool

```text
BeautyAgent
  → search_knowledge(query)
  → RAGTool
  → Retriever
  → context + sources
  → Tool Observation
  → BeautyAgent LLM
```

RAGTool 不调用 RAGService 生成第二个最终答案。最终回答仍由 BeautyAgent 或 Workflow 的 FinalAnswer 生成。

当前 VectorStore 是本地 JSON 持久化和内存相似度搜索，不是生产级 Vector Database。

## 10. Memory Architecture

```text
MemoryStore
  → sessions: dict[session_id, ConversationMemory]
  → ConversationMemory.messages
```

当前能力：

- 同一 BeautyAgent/MemoryStore 实例内的短期消息上下文。
- 同一次规划工作流中，各 PlanStep 使用相同 session_id 和 Agent 实例。

当前限制：

- FastAPI `get_agent()` 每次创建新的 MemoryStore。
- 相同 session_id 不能跨 HTTP 请求恢复消息。
- 没有持久化 Memory、User Profile 或 Long-term Memory。

## 11. Error Propagation

- Repository 文件错误转换为 `IngredientDataError`。
- Retriever 将内部检索错误包装为 `RetrieverError`。
- ToolExecutor 将参数或工具执行错误包装为 Agent Tool 异常。
- AgentStepExecutor 将 Agent 错误包装为 `AgentStepExecutionError`。
- PlanExecutor 将单步错误包装为 `PlanExecutionError` 并把步骤标为 FAILED。
- WorkflowRunner 在已有 WorkflowState 后捕获异常，写入 FAILED 和 error，然后继续向上抛出。
- Planning Gate API 将异常转换为通用 HTTP 500。

业务判断失败 `ValidationResult(success=False)` 不应被当成系统异常，但其 Recovery 处理目前尚未完成。

## 12. Test Contract Status

与当前实现匹配的测试主要覆盖：

- Ingredient Model / Repository / Service / 基础 API
- BeautyAgent 无 Tool、Business Tool、RAG Tool 和 Multi Tool 行为
- Cosine Similarity、VectorStore、Retriever、RAGTool
- Planner 和 Plan 模型
- PlanningGate SIMPLE / COMPLEX 组件级路由
- Validator 独立 JSON 契约
- 部分 WorkflowRunner 成功和错误状态行为

当前测试目录也存在接口漂移：

- 部分测试仍只用 Plan 调用 `PlanExecutor.execute()`。
- 部分测试仍向 `AgentStepExecutor.__init__()` 传入 session_id 和 goal。
- 部分 WorkflowRunner 测试未传 validator 或 recovery_manager。
- Recovery 测试描述了目标契约，但当前生产代码尚未满足。

因此测试文件的存在不能被解释为整个 Planning/Recovery 生产链已完成。

## 13. Current Incomplete Capabilities

### 🔴 生产链路未完成

- Planning Gate 的 WorkflowRunner/RecoveryManager 依赖装配
- Validation Failure 的稳定返回类型
- Reflection 真实实现
- Replanner 真实实现
- RecoveryManager / RecoveryWorkflow / PlanExecutor / FinalAnswer 接口统一
- Recovery 后二次 Validation
- Recovery 成功或失败后的 WorkflowResult 构造

### 尚未实现的产品能力

- 跨请求持久化 Session Memory
- User Profile
- Long-term Memory
- 生产级 Vector Database
- 大规模专业知识库治理
- Docker 和生产部署

## 14. Documentation Governance

- 本文件只记录已经存在的代码和当前断点。
- 未完成能力必须明确标记，不能放入 Completed 列表。
- README 只做项目介绍，并链接本文获取详细架构。
- docs 目录中的 `*PHASE5_COMPLETE.md` 保留为历史记录，不再更新为当前事实来源。
- 架构或接口发生变化时，应先同步本文中的数据流、组件契约和状态矩阵。
