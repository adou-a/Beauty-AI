from src.exceptions.llm_exception import LLMConnectionError
from src.ai.llm_client import LLMClient

import pytest


def test_llm_error():
    client = LLMClient()

    with pytest.raises(LLMConnectionError):
        client.chat('test')