from ..config.settings import OPENAI_API_KEY


class LLMClient:

    def __init__(self) -> None:
        self.api_key = OPENAI_API_KEY


    def generate(
        self,
        prompt: str
    ) -> str:

        """
        调用大模型生成内容
        """

        raise NotImplementedError