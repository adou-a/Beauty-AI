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
- Knowledge Base
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

## 已完成阶段

### Phase 1：Python Engineering

状态：**完成**

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

### Phase 2：FastAPI Backend

状态：**完成**

完成：

- HTTP / REST
- GET / POST
- Router
- Pydantic Schema
- Dependency Injection
- HTTP Exception
- Swagger
- API Testing

### Phase 3：LLM Engineering

状态：**完成**

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

### Phase 4：AI Agent Core

状态：**完成**

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

## 当前系统定位

Beauty-AI 当前已经属于：

```text
垂直领域 AI Agent MVP
```

核心流程：

```text
User
 ↓
FastAPI
 ↓
BeautyAgent
 ↓
Conversation Context
 ↓
DeepSeek
 ↓
Tool Calling
 ↓
Tool Executor
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

## 下一阶段

# Phase 5：RAG + Knowledge Base

目标：

让 Beauty-Agent 从“会调用工具”升级为“会主动检索专业知识”。

计划能力：

- Document Knowledge Base
- Chunking
- Embedding
- Vector Database
- Similarity Search
- Retriever
- RAG Pipeline
- RAG Tool
- Agent + RAG
- RAG Testing
