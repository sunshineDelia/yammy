# 收藏模块实现报告

- 职责：收藏增删查与状态查询，按匿名设备标识 `X-Device-Id` 持久化，无需登录。
- 分层：`model.py`（Favorite，唯一约束）、`schema.py`、`repository.py`（get/add/delete/list）、`service.py`（幂等/目标校验/列表聚合）、`router.py`。
- 接口：`GET /api/favorites`、`POST /api/favorites`、`DELETE /api/favorites/{target_type}/{target_id}`、`GET /api/favorites/status`。
- 测试：`tests/test_favorite.py`（13 用例，覆盖增删查/幂等/非法 target_type/景点分支/status/缺失设备标识）。
