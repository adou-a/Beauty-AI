# Beauty-AI Architecture

## 当前架构

``` text
Client
 |
HTTP Request
 |
FastAPI
 |
Router
 |
Depends()
 |
Service
 |
Repository
 |
Ingredient Model
 |
Knowledge Data
```

## 模块职责

### API Layer

负责： - HTTP请求接收 - 参数验证 - 返回响应 - 异常转换

### Service Layer

负责： - 业务逻辑 - 成分查询 - 分析流程

不依赖HTTP。

### Repository Layer

负责： - 数据读取 - 数据访问

不直接暴露给API。

### Model

负责： - 业务数据结构定义

## AI扩展方向

未来：

User ↓ FastAPI ↓ AIService ↓ LLMClient ↓ Tools ↓ Knowledge Base
