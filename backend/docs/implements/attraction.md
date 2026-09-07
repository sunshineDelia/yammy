# 景点模块实现报告

- 职责：景点列表/详情/搜索，含评分、评价数、景区等级、建议时长、地址、标签等详细资料。
- 分层：`model.py`（Attraction）、`schema.py`（AttractionOut/AttractionListOut/AttractionBrief）、`repository.py`（list/get_by_id/list_all/search/get_by_ids）、`service.py`、`router.py`。
- 接口：`GET /api/attractions`（分页/搜索/好评排序 sort=rating）、`GET /api/attractions/{id}`。
- 测试：`tests/test_attraction.py`（10 用例，覆盖列表/搜索/详情/404/分页边界/好评排序）。
