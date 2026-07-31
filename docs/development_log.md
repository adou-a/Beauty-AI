# Beauty-AI Development Log


## 2026-07-29

### 完成内容

- 完善 Ingredient Model
- Repository实现JSON转换Model
- Service改为使用Ingredient对象
- 添加Type Hint
- 完善Repository
- test功能和结构
- Exception Handing
- Logging
- Settings
- LLM接口预留
### 修改原因

之前的数据流程：

JSON
 ↓
Repository
 ↓
dict
 ↓
Service


存在问题：

- Service直接依赖JSON字段
- 数据结构不稳定
- 后续无法扩展数据库
- Agent 需要知道：出现异常的原因，不能全是Exception


修改后：

JSON
 ↓
Repository
 ↓
Ingredient对象
 ↓
Service


### 遇到的问题

问题：

运行pytest出现：

ModuleNotFoundError: No module named 'src'


原因：

项目没有安装为Python package。


解决：

添加：

pyproject.toml

执行：

pip install -e .


### 学到的知识

- Python package结构
- Repository职责
- Model作用
- Type Hint使用
- dataclass
- assert isinstance(A,B)
2026-07-30

完成：
1. Ingredient Model
2. Repository重构
3. Service重构
4. Exception系统
5. Logging
6. AI接口预留

获得能力：
理解Python分层架构
理解LLM与业务解耦
2026-07-31
Pydantic Model