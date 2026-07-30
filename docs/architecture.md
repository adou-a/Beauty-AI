# Beauty-AI Architecture


## 当前架构


User

↓

Service

↓

Repository

↓

JSON Database



## 数据流


ingredients.json

↓

IngredientRepository

↓

Ingredient Model

↓

IngredientService



## 各层职责


### Repository

负责：

- 数据读取
- 数据转换


不负责：

- 业务逻辑


### Model

负责：

- 定义数据结构


### Service

负责：

- 查询
- 判断
- 推荐逻辑