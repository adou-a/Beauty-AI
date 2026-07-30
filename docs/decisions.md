# Technical Decisions


## 为什么使用Repository？


问题：

Service直接读取JSON。


缺点：

以后换数据库需要修改大量代码。


决定：

增加Repository层。


结果：

未来：

JSON

可以替换成：

MySQL

MongoDB

API


Service无需修改。



---

## 为什么使用Model？


问题：

dict字段容易混乱。


决定：

创建Ingredient class。


结果：

统一数据结构。


### Exception Handling
问题
建立自定义异常
文件、数据和查询异常是否可控