# AI 咨询模块实现报告

- 职责：DeepSeek 游玩咨询，注入本地美食/景点数据，一次性返回。
- 分层：`schema.py`（ConsultRequest/ConsultResponse）、`deepseek_client.py`（懒初始化 OpenAI 客户端）、`context_builder.py`（实体名反向匹配 + LIKE 兜底，构建 prompt）、`service.py`（consult）、`router.py`。
- 接口：`POST /api/ai/consult`。
- 测试：`tests/test_ai.py`（4 用例，mock DeepSeek，校验答案/上下文注入/422/502）。
