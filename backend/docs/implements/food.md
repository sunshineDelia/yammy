# 美食模块实现报告

- 职责：美食列表/详情/搜索，含推荐门店、评分、评价数、分类、标签、商圈等详细资料。
- 分层：`model.py`（Food/Store）、`schema.py`（StoreOut/FoodOut/FoodListOut/FoodBrief）、`repository.py`（list/get_by_id/list_all/search/get_by_ids）、`service.py`（list_foods/get_food）、`router.py`。
- 接口：`GET /api/foods`（分页 page/page_size、关键字搜索 keyword、好评排序 sort=rating）、`GET /api/foods/{id}`（含推荐门店）。
- 测试：`tests/test_food.py`（10 用例，覆盖列表/搜索/详情含门店/404/分页边界/好评排序/非法排序）。
