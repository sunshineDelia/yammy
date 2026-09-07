from openai import OpenAI

from app.core.config import settings


class DeepSeekClient:
    """懒初始化 OpenAI 客户端，测试可打桩 chat 方法而无需真实 key。"""

    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
        return self._client

    def chat(self, messages: list[dict]) -> str:
        resp = self.client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
        )
        return resp.choices[0].message.content or ""
