# Beauty-AI

## 项目介绍

Beauty-AI 是一个基于 Python 开发的智能护肤成分分析助手。

项目目标是构建一个结合：

* 护肤成分知识库
* AI 分析能力
* Agent 工作流

的智能护肤分析系统。

用户可以输入护肤成分信息，系统通过成分数据库分析：

* 成分作用
* 适合肤质
* 使用风险
* 护肤建议

目前项目已经完成 Python 工程化重构，并正在向 AI Agent 应用方向扩展。

---

# 当前项目状态

## 已完成

### Python 工程化

* ✅ 成分数据库管理
* ✅ JSON 数据读取
* ✅ Ingredient 数据模型
* ✅ Repository 数据访问层
* ✅ Service 业务处理层
* ✅ Type Hint 类型管理
* ✅ 自定义异常系统
* ✅ Logging 日志系统
* ✅ 配置管理

### FastAPI 后端

* ✅ FastAPI 服务搭建
* ✅ API 路由分层
* ✅ GET 查询接口
* ✅ POST 请求接口
* ✅ Pydantic Request / Response Model
* ✅ Dependency Injection 依赖注入
* ✅ HTTP 异常处理
* ✅ API 自动文档 Swagger

### 测试

* ✅ Model 测试
* ✅ Repository 测试
* ✅ Service 测试
* ✅ Exception 测试
* ✅ API 测试

---

# 开发中

下一阶段：

* ⬜ 接入 LLM API
* ⬜ AIService 实际调用大模型
* ⬜ Prompt 工程
* ⬜ Tool Calling
* ⬜ Agent 工作流
* ⬜ 知识库增强（RAG）

---

# 项目结构

```
Beauty-AI

├── data
│   └── ingredients.json
│
├── docs
│   ├── architecture.md
│   ├── decisions.md
│   └── development_log.md
│
├── src
│   │
│   ├── api
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── dependencies.py
│   │
│   ├── ai
│   │   ├── llm_client.py
│   │   └── ai_service.py
│   │
│   ├── models
│   │   └── ingredient.py
│   │
│   ├── services
│   │   ├── ingredient_repository.py
│   │   └── ingredient_service.py
│   │
│   ├── exceptions
│   │   └── ingredient_exception.py
│   │
│   ├── config
│   │   └── settings.py
│   │
│   └── utils
│       └── logger.py
│
├── tests
│   ├── test_model.py
│   ├── test_repository.py
│   ├── test_service.py
│   ├── test_exception.py
│   └── test_api.py
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# 技术栈

## Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

## Project Engineering

* Repository Pattern
* Service Layer
* Dependency Injection
* Exception Handling
* Logging
* Pytest

## AI Architecture

当前已预留：

* LLM Client
* AI Service

未来支持：

* 大语言模型调用
* Agent Tool
* RAG

---

# 环境要求

Python >= 3.11

推荐环境：

* Windows / Linux / macOS
* VS Code

---

# Installation

Clone project:

```bash
git clone xxx
```

进入项目：

```bash
cd Beauty-AI
```

安装依赖：

```bash
pip install -r requirements.txt
```

---

# 环境变量

创建：

```
.env
```

配置：

```
OPENAI_API_KEY=your_api_key
```

---

# 运行项目

## 启动 FastAPI 服务

```bash
python -m uvicorn src.api.main:app --reload
```

服务启动后：

访问：

```
http://127.0.0.1:8000
```

API 文档：

```
http://127.0.0.1:8000/docs
```

---

# API 示例

## 查询成分

请求：

```
GET /ingredients/{name}
```

例如：

```
GET /ingredients/烟酰胺
```

返回：

```json
{
    "chinese_name": "烟酰胺",
    "risk_level": "低",
    "functions": [
        "改善肤色",
        "支持皮肤屏障"
    ]
}
```

---

## AI分析接口

请求：

```
POST /analyze
```

示例：

```json
{
    "ingredient": "烟酰胺",
    "skin_type": "敏感肌"
}
```

当前接口已完成数据接收设计。

未来将连接：

```
AIService
    |
LLMClient
    |
大语言模型
```

---

# 测试

运行：

```bash
pytest
```

测试覆盖：

* Model
* Repository
* Service
* Exception
* API

---

# 开发路线

## Phase 1：Python工程化

已完成：

```
JSON
 ↓
Repository
 ↓
Service
 ↓
Model
```

---

## Phase 2：Backend API

已完成：

```
Client
 ↓
FastAPI
 ↓
Router
 ↓
Service
 ↓
Repository
```

---

## Phase 3：AI能力接入

计划：

```
User

 ↓

FastAPI

 ↓

AIService

 ↓

LLMClient

 ↓

Agent

 ↓

Tools / Knowledge Base
```

---

# 项目目标

Beauty-AI 的最终目标：

构建一个具备：

* 知识检索
* AI分析
* 工具调用
* 工作流管理

能力的垂直领域 AI Agent。
