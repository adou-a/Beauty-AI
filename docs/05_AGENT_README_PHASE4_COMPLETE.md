# Beauty-Agent README

## Agent 简介

Beauty-Agent 是 Beauty-AI 在 **Phase 4：AI Agent Core** 实现的核心 Agent。

它不是让 DeepSeek 直接回答问题，而是让模型根据用户目标自主决定是否调用系统能力。

核心：

```text
LLM + Agent Loop + Tools + Memory + Testing
```

## 当前能力

- DeepSeek Tool Calling
- Agent Loop
- Tool Schema
- Tool Registry
- Tool Executor
- Multi Tool
- Tool Result Observation
- Ingredient Service / Repository 接入
- FakeLLM Testing
- FastAPI Agent API
- Short-term Conversation Memory
- Session Context
- Agent Exception
- Agent Logging

## Agent 架构

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
Tools
 ↓
Service
 ↓
Repository
 ↓
Knowledge Data
 ↓
Tool Result
 ↓
BeautyAgent
 ↓
DeepSeek
 ↓
Final Answer
```

## Agent Loop

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

## Tool Calling

普通函数调用：

```text
程序决定调用哪个函数
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

LLM 决定“需要什么能力”，Python 负责真正执行。

## 当前 Tools

### search_ingredient

用途：

查询护肤成分信息。

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

### check_skin_risk

用途：

根据肤质提供基础风险提示。

```json
{
  "name": "check_skin_risk",
  "description": "提醒皮肤需要注意刺激性",
  "parameters": {
    "skin_type": "string"
  }
}
```

## Tool Schema

位置：

```text
src/agent/schemas.py
```

作用：

给 DeepSeek 提供工具说明。

包含：

- Tool 名称
- 描述
- 参数
- 参数类型
- required

Schema 不执行代码。

## Tool Registry

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

它让 Agent 不需要直接依赖具体函数。

## Tool Executor

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

## Tool 与 Service

Service：

```text
系统业务逻辑
```

Tool：

```text
Agent 的能力接口
```

正确：

```text
Agent → Tool → Service → Repository
```

## Memory

当前：

```text
Short-term Conversation Memory
```

用途：

让同一 Session 理解前文。

未来：

- Persistent Memory
- User Profile
- Long-term Memory

## FastAPI Agent API

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
- Execution

## Dependency Injection

Agent 依赖：

```text
Repository
Service
Tool
Registry
Executor
LLM
Memory
```

组装：

```text
Repository
 ↓
Service
 ↓
Tool
 ↓
Registry
 ↓
Executor
 ↓
LLMClient
 ↓
BeautyAgent
```

测试时：

```text
Real LLM → FakeLLM
```

## FakeLLM Testing

Agent 测试重点是行为。

需要验证：

- 是否调用 Tool
- Tool 是否正确
- 参数是否正确
- Observation 是否加入 messages
- 是否继续 Loop
- 无 Tool 时是否返回
- 错误 Tool 是否抛异常

FakeLLM 优点：

- 不消耗 Token
- 不依赖网络
- 输出稳定
- 测试快
- 易于模拟异常

## Agent Exception

需要区分：

```text
AgentError
ToolNotFoundError
ToolExecutionError
LLMError
MemoryError
```

## Agent Logging

建议记录：

```text
Agent received request
LLM decision received
Selected tool
Executing tool
Tool completed
Observation appended
Final response generated
```

## 示例

用户：

```text
我是油敏肌，烟酰胺适合我吗？
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
check_skin_risk("油敏肌")
 ↓
Observation
 ↓
DeepSeek 综合
 ↓
Final Answer
```

## 当前状态

Phase 4：**完成**

当前定位：

```text
Agent Core MVP
```

## 下一阶段

# Phase 5：RAG + Knowledge Base

升级：

```text
Agent + Tools + Memory
```

到：

```text
Agent + Tools + Memory + RAG
```

目标：

```text
BeautyAgent
 ↓
RAG Tool
 ↓
Retriever
 ↓
Vector Database
 ↓
Knowledge Base
 ↓
Context
 ↓
DeepSeek
 ↓
Final Answer
```
