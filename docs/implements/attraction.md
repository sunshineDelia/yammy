# 景点模块实现报告

- 职责：景点列表/详情/搜索。
- 分层：`model.py`（Attraction）、`schema.py`（AttractionOut/AttractionListOut/AttractionBrief）、`repository.py`（list/get_by_id/list_all/search）、`service.py`、`router.py`。
- 接口：`GET /api/attractions`、`GET /api/attractions/{id}`。
- 测试：`tests/test_attraction.py`（4 用例）。
