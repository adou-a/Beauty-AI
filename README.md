# Beauty-AI
## 项目介绍

Beauty-AI 是一个基于 Python 开发的智能护肤成分分析助手。

用户可以输入护肤成分名称，
系统通过成分数据库分析：

- 成分作用
- 适合肤质
- 使用风险
- 护肤建议

项目目前正在接入大语言模型，

## 项目功能

目前已实现：

- ✅ 成分数据库管理
- ✅ JSON 数据读取
- ✅ Ingredient 数据模型
- ✅ Repository 数据访问层
- ✅ Service 业务处理层
- ✅ 成分查询
- ✅ 肤质匹配
- ✅ 功效分类查询
- ✅ 自定义异常处理
- ✅ Logging 日志系统

开发中：

- ⬜ LLM 接入
- ⬜ AI 自动分析
- ⬜ Agent Tool

Beauty-AI
│
├── data
│   └── ingredients.json
│
├── src
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
│   ├── utils
│   │   └── logger.py
│   │
│   └── main.py
│
├── tests
│
├── requirements.txt
└── README.md

## 环境要求

Python >= 3.11

推荐环境：

- Windows / Linux / macOS
- VS Code

## Installation

Clone project:

git clone xxx


Install dependencies:

pip install -r requirements.txt


##  运行
python -m src.main


## Test

运行测试：tests

pytest