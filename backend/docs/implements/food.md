# 美食模块实现报告

- 职责：美食列表/详情/搜索，含推荐门店。
- 分层：`model.py`（Food/Store）、`schema.py`（StoreOut/FoodOut/FoodListOut/FoodBrief）、`repository.py`（list/get_by_id/list_all/search）、`service.py`（list_foods/get_food）、`router.py`。
- 接口：`GET /api/foods`、`GET /api/foods/{id}`。
- 测试：`tests/test_food.py`（4 用例，覆盖列表/搜索/详情含门店/404）。
