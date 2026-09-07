# AI 咨询模块实现报告

- 职责：DeepSeek 游玩咨询，注入本地美食/景点数据（实体名反向匹配 → 关键词 LIKE → Top5 兜底），一次性返回。
- 分层：`schema.py`（ConsultRequest/ConsultResponse）、`deepseek_client.py`（懒初始化 OpenAI 客户端 + DeepSeekError）、`context_builder.py`（检索与 prompt 构建）、`service.py`（consult）、`router.py`。
- 接口：`POST /api/ai/consult`，响应含 `answer` 与可跳转的 `references`（foods/attractions，带 id）。
- 测试：`tests/test_ai.py`（8 用例，mock DeepSeek，覆盖答案/上下文注入/兜底/422/502/具体问题不越界）。
