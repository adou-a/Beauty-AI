# Beauty-AI Architecture

## 当前整体架构

``` text
Client

↓

FastAPI

↓

Router

↓

AIService

↓

IngredientService

↓

Repository

↓

Knowledge Data


AIService

↓

LLMClient

↓

DeepSeek API

↓

Structured Output
```

## 模块职责

### API Layer

负责：

-   HTTP 请求接收
-   参数验证
-   返回响应
-   异常转换

不负责：

-   Prompt设计
-   LLM调用

------------------------------------------------------------------------

### AIService Layer

负责：

-   AI业务流程
-   Prompt构建
-   知识融合
-   调用LLMClient
-   输出分析结果

------------------------------------------------------------------------

### LLMClient Layer

负责：

-   DeepSeek API通信
-   模型配置
-   请求异常处理
-   日志记录

不负责：

-   护肤业务逻辑

------------------------------------------------------------------------

### Repository Layer

负责：

-   数据读取
-   数据访问

不直接暴露给API。

------------------------------------------------------------------------

### Model Layer

负责：

-   业务数据结构定义
-   AI输出结构定义

## AI扩展方向

未来：

User

↓

FastAPI

↓

AI Agent

↓

Tools

↓

Knowledge Base

↓

RAG

↓

Memory
