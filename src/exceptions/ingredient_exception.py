# 创建自定义异常

class IngredientError(Exception):
    """
    成分相关基础异常
    """
    pass


class IngredientDataError(IngredientError):
    """
    成分数据加载失败
    """
    pass


class IngredientNotFoundError(IngredientError):
    """
    成分不存在
    """
    pass