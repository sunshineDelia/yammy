from openai import OpenAI

from app.core.config import settings


class DeepSeekError(Exception):
    """DeepSeek 调用失败时抛出，供路由层映射为 502。"""


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
        try:
            resp = self.client.chat.completions.create(
                model=settings.deepseek_model,
                messages=messages,
            )
        except Exception as exc:
            raise DeepSeekError(str(exc)) from exc
        return resp.choices[0].message.content or ""
