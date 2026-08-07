# Beauty-AI Architecture

## 当前整体架构

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
  +----------------------+
  |                      |
  v                      v
Memory                  LLMClient
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
                  +-------+-------+
                  |               |
                  v               v
        search_ingredient   check_skin_risk
                  |
                  v
          IngredientService
                  |
                  v
       IngredientRepository
                  |
                  v
          Knowledge Data
```

## 请求流程

```text
1. User 输入问题
2. FastAPI 接收请求
3. Router 处理 HTTP
4. Dependency Injection 提供 BeautyAgent
5. Agent 加载 Conversation Context
6. Agent 调用 LLMClient
7. DeepSeek 判断是否需要 Tool
8. DeepSeek 返回 tool_call
9. ToolExecutor 解析工具名称和参数
10. ToolRegistry 找到 Tool
11. Tool 执行业务能力
12. Service / Repository 获取数据
13. Tool Result 作为 Observation 返回 Agent
14. Agent 将 Observation 加入 messages
15. Agent 再次调用 DeepSeek
16. 如仍需要工具则继续循环
17. 无 tool_call 时返回 Final Answer
```

## 模块职责

### API Layer

负责：

- HTTP 请求
- 参数验证
- Response
- Router
- Dependency Injection
- HTTP Exception
- Swagger

不负责 Agent 决策和业务逻辑。

### BeautyAgent

负责：

- 接收用户输入
- Agent Loop
- messages
- 调用 LLM
- 判断 tool_calls
- 加入 Tool Observation
- 控制继续执行或返回

核心：

```text
Think → Act → Observe → Think → Answer
```

### LLMClient

默认模型：DeepSeek

负责：

- DeepSeek API
- messages
- tools schema
- tool_calls / content
- 模型配置
- LLM Exception
- Logging

### Tool Schema

文件：

```text
src/agent/schemas.py
```

告诉 LLM：

- Tool 名称
- Tool 描述
- 参数
- 参数类型

当前：

- search_ingredient
- check_skin_risk

### Tool Registry

文件：

```text
src/agent/registry.py
```

负责：

- register
- get
- get_tools
- exists

### Tool Executor

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

### Tool Layer

文件：

```text
src/agent/tools.py
```

#### search_ingredient

```text
search_ingredient
 ↓
IngredientService
 ↓
IngredientRepository
 ↓
ingredients.json
```

#### check_skin_risk

根据肤质提供基础风险提示。

### Service Layer

负责业务逻辑，不依赖 HTTP 和 Agent。

### Repository Layer

负责数据访问。

正确关系：

```text
Agent
 ↓
Tool
 ↓
Service
 ↓
Repository
```

### Memory Layer

当前完成：

- Short-term Conversation Memory
- Session Context

未来：

- Persistent Memory
- User Profile
- Long-term Memory

### Exception Layer

区分：

- Ingredient Exception
- LLM Exception
- Agent Exception
- Tool Exception

### Logging Layer

需要记录：

```text
Request received
LLM decision
Tool selected
Tool executing
Tool completed
Final response generated
```

## 当前设计原则

1. Agent 不直接访问数据库
2. Tool 不重复实现 Service
3. LLMClient 只负责模型通信
4. Registry 管理工具
5. Executor 独立执行工具
6. FakeLLM 测试 Agent 行为
7. Memory 与 Agent 决策分离
8. Router 不写业务逻辑
9. DeepSeek 可替换
10. 各层职责清晰

## Phase 5 扩展

```text
BeautyAgent
    |
    +------------------+
    |                  |
    v                  v
Business Tools      RAG Tool
                       |
                       v
                    Retriever
                       |
                       v
                 Vector Database
                       |
                       v
                 Knowledge Base
```
