import logging


def get_logger(name: str):

    logger = logging.getLogger(name)
    #设置这个Logger最低接受什么级别的日志
    logger.setLevel(logging.INFO)
    #只有第一次配置Logger时才添加Handler
    if not logger.handlers:
        #把日志输出到终端
        handler = logging.StreamHandler()
        #日志格式
        formatter = logging.Formatter(
            "%(levelname)s %(name)s:\n%(message)s"
        )
        #给这个Handler指定刚刚创建的日志格式
        handler.setFormatter(formatter)
        #连接handler到Logger上
        logger.addHandler(handler)

    return logger

f'''
get_logger("src.agent.agent")
        │
        ↓
logging.getLogger("src.agent.agent")
        │
        ↓
拿到 Logger
        │
        ↓
设置最低日志等级 INFO
        │
        ↓
检查有没有 Handler
        │
        ├── 有
        │    ↓
        │   不重复创建
        │
        └── 没有
             ↓
        创建 StreamHandler
             ↓
        创建 Formatter
             ↓
        Formatter 装到 Handler
             ↓
        Handler 装到 Logger
             ↓
        return logger
'''