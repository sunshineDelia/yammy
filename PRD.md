# 南昌旅游美食推荐平台 — 产品需求文档（PRD）

| 项目 | 内容 |
|------|------|
| 文档版本 | v1.0 |
| 编写日期 | 2026-09-07 |
| 状态 | 待评审 |
| 产品形态 | PC 端网站（仅桌面端，不做移动端适配） |
| 目标用户 | 来南昌旅游的游客（免登录，匿名访问） |

---

## 1. 项目概述

### 1.1 背景与目标

南昌是江西省省会，拥有滕王阁、八一广场等旅游资源，以及瓦罐汤、南昌拌粉、藜蒿炒腊肉等特色美食。现有旅游信息分散、缺乏一站式的「美食 + 景点 + AI 攻略」聚合平台。

本平台面向来南昌旅游的游客，提供：

1. 南昌特色美食的集中展示与门店推荐；
2. 南昌旅游景点的集中展示（含开放时间、门票参考）；
3. 基于大模型的 AI 游玩咨询，结合平台本地数据给出个性化攻略；
4. 免登录的收藏能力，方便游客保存感兴趣的美食与景点。

### 1.2 产品定位

一款**纯 PC 端、免登录、只读浏览为主**的南昌本地旅游美食信息与智能咨询网站。

### 1.3 核心价值

- **信息聚合**：美食 + 景点一站式浏览。
- **智能咨询**：AI 基于平台真实数据回答问题，而非通用泛泛而谈。
- **零门槛**：无需注册登录，打开即用。

---

## 2. 范围界定

### 2.1 本期范围（In Scope）

- 美食列表浏览与详情（含推荐门店、真实图片）
- 景点列表浏览与详情（含真实图片）
- AI 游玩咨询（一次性问答）
- 收藏与「我的收藏」列表
- 后端分层 + 全部 API 单元测试
- 各模块实现报告输出至 `docs/implements`

### 2.2 非目标（Out of Scope）

- 移动端 / 响应式适配
- 用户注册、登录、鉴权体系
- 美食/景点的后台管理（增删改），数据仅通过预置种子数据提供
- AI 对话历史持久化（咨询为无状态问答）
- 评论、评分、UGC 内容
- 支付、预订、跳转第三方交易
- 多语言、国际化

---

## 3. 功能需求

### 3.1 南昌特色美食列表

**功能描述**：展示南昌特色美食，供游客浏览。

**数据字段**：

| 字段 | 说明 | 类型 | 必填 |
|------|------|------|------|
| 名称 | 美食名称，如「南昌拌粉」 | string | 是 |
| 简介 | 美食介绍（口味、历史、特色） | string | 是 |
| 人均消费 | 参考人均价格（元） | number | 是 |
| 推荐门店 | 该美食的推荐就餐门店 | 门店列表 | 是 |

**交互**：

- 列表页分页展示美食卡片（名称、简介摘要、人均消费、图片占位）。
- 支持按关键字搜索（名称/简介）。
- 点击进入详情页，展示完整简介与全部推荐门店。
- 每条美食支持「收藏」操作（见 3.4）。

### 3.2 南昌旅游景点列表

**功能描述**：展示南昌旅游景点，供游客规划行程。

**数据字段**：

| 字段 | 说明 | 类型 | 必填 |
|------|------|------|------|
| 名称 | 景点名称，如「滕王阁」 | string | 是 |
| 简介 | 景点介绍（历史、看点） | string | 是 |
| 开放时间 | 营业/开放时间，如「08:00-18:00」 | string | 是 |
| 门票参考 | 门票参考价，如「50 元 / 免费」 | string | 是 |

> 「门票参考」为文本类型，支持「免费」「淡季/旺季」等灵活表达。

**交互**：

- 列表页分页展示景点卡片（名称、简介摘要、开放时间、门票参考）。
- 支持按关键字搜索（名称/简介）。
- 点击进入详情页。
- 每个景点支持「收藏」操作（见 3.4）。

### 3.3 AI 游玩咨询

**功能描述**：用户输入问题，系统调用 DeepSeek 大模型，**结合平台本地美食/景点数据**给出南昌旅游美食攻略建议。

**交互**：

- 咨询页提供输入框，用户输入自然语言问题（如「帮我规划一天南昌美食行程」「滕王阁周边有什么好吃的」）。
- 提交后等待返回，展示 AI 回答；若检索到相关美食/景点，同时展示「相关推荐」卡片（可跳转详情/收藏）。
- 回答方式为**一次性返回**（非流式），期间展示加载态。

**回答依据**（已确认）：**注入本地数据**。后端先从数据库检索与问题相关的美食/景点，作为上下文拼入 prompt，再调用 DeepSeek，使回答与平台数据一致、可追溯。

### 3.4 收藏功能

**功能描述**：游客可收藏美食/景点，并在「我的收藏」中查看。

**持久化方式**（已确认）：**服务端按设备标识存储**。

- 前端首次访问时生成匿名设备 ID（UUID），存入 `localStorage`，随请求通过 `X-Device-Id` 请求头携带。
- 后端以此设备 ID 关联收藏，不依赖登录。
- 设备 ID 仅标识浏览器/设备，不采集个人身份信息。

**交互**：

- 美食/景点卡片与详情页均有「收藏/已收藏」切换按钮。
- 「我的收藏」页分页展示已收藏的美食与景点，支持取消收藏。

---

## 4. 数据模型

### 4.1 表结构

#### `food`（美食）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| name | VARCHAR(100) | NOT NULL | 美食名称 |
| description | TEXT | NOT NULL | 简介 |
| avg_price | DECIMAL(10,2) | NOT NULL | 人均消费（元） |
| image_url | VARCHAR(255) | NULL | 图片相对路径（静态资源，如 /static/images/foods/banfen.jpg） |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

#### `store`（推荐门店）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| food_id | BIGINT | FK → food.id, NOT NULL | 所属美食 |
| name | VARCHAR(100) | NOT NULL | 门店名称 |
| address | VARCHAR(255) | NULL | 门店地址（可选） |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

#### `attraction`（景点）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| name | VARCHAR(100) | NOT NULL | 景点名称 |
| description | TEXT | NOT NULL | 简介 |
| open_time | VARCHAR(100) | NOT NULL | 开放时间 |
| ticket_price | VARCHAR(100) | NOT NULL | 门票参考（文本） |
| image_url | VARCHAR(255) | NULL | 图片相对路径（静态资源，如 /static/images/foods/banfen.jpg） |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

#### `favorite`（收藏）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| device_id | VARCHAR(64) | NOT NULL, 有索引 | 匿名设备标识 |
| target_type | VARCHAR(20) | NOT NULL | 收藏对象类型：`food` / `attraction` |
| target_id | BIGINT | NOT NULL | 收藏对象 ID |
| created_at | DATETIME | DEFAULT NOW | 收藏时间 |

**唯一约束**：`UNIQUE(device_id, target_type, target_id)`，保证同一设备对同一对象不重复收藏。

> `target_type` + `target_id` 为多态关联，不设外键，由 service 层校验目标是否存在。

### 4.2 数据来源

美食/景点数据为**预置种子数据**：随项目提供 `seed/` 目录下的初始化脚本（SQL 或 Python），首次部署执行后即可浏览，前端只读，无管理入口。

### 4.3 图片资源方案（已确认：真实图）

- **存储**：美食/景点使用真实图片，作为静态资源随项目内置，存放于 `backend/static/images/{foods,attractions}/`。
- **字段**：`image_url` 存图片相对路径（如 `/static/images/foods/banfen.jpg`），前端直接以 `<img>` 引用。
- **服务**：FastAPI 通过 `StaticFiles` 挂载 `/static` 目录对外提供图片。
- **来源与版权**：图片来自项目内置的真实图片资源（由用户提供，或从可商用免费图库如 Unsplash / Pexels 下载）；禁止使用未授权图片。种子数据脚本同时写入 DB 记录与对应图片文件。

---

## 5. 系统架构

### 5.1 技术栈

| 层 | 技术 |
|----|------|
| 前端 | 原生 HTML + CSS + JavaScript（无框架） |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | MySQL |
| AI | DeepSeek 大模型（`deepseek-chat`，模型名可配置） |
| 测试 | pytest + FastAPI TestClient + SQLite（测试库）+ mock |

### 5.2 总体结构

```
游客浏览器（PC）
   │  HTTP + JSON
   ▼
FastAPI 后端
   ├─ Router 层（路由、参数校验、响应序列化）
   ├─ Service 层（业务逻辑、编排）
   ├─ Repository 层（数据访问）
   └─ AI 客户端（DeepSeek）
   ▼
MySQL
```

### 5.3 后端分层与模块划分

**约束**：后端分层 router / service / repository；**一个模块一个包**（每个业务模块为独立包，自含其 router/service/repository/model/schema）。

```
backend/
├─ app/
│  ├─ main.py                 # FastAPI 入口、路由注册、CORS、静态资源挂载
│  ├─ core/
│  │  ├─ config.py            # 配置（Settings，读取 .env）
│  │  ├─ database.py          # 引擎、SessionLocal、Base
│  │  └─ deps.py              # 依赖注入（get_db 等）
│  └─ modules/
│     ├─ food/                # 美食模块（一个包）
│     │  ├─ model.py
│     │  ├─ schema.py
│     │  ├─ repository.py
│     │  ├─ service.py
│     │  └─ router.py
│     ├─ attraction/          # 景点模块
│     │  └─ （同 food 结构）
│     ├─ ai/                  # AI 咨询模块
│     │  ├─ schema.py
│     │  ├─ deepseek_client.py   # DeepSeek 调用封装
│     │  ├─ context_builder.py   # 本地数据检索与 prompt 构建
│     │  ├─ service.py
│     │  └─ router.py
│     └─ favorite/            # 收藏模块
│        └─ （同 food 结构）
├─ seed/                      # 预置种子数据脚本
├─ static/                    # 静态图片（真实图）
│  ├─ images/foods/           # 美食图片
│  └─ images/attractions/     # 景点图片
├─ tests/                     # 单元测试
│  ├─ conftest.py
│  ├─ test_food.py
│  ├─ test_attraction.py
│  ├─ test_ai.py
│  └─ test_favorite.py
├─ requirements.txt
├─ .env.example
└─ README.md
```

### 5.4 前端结构

```
frontend/
├─ index.html          # 单页入口（导航：首页 / 美食 / 景点 / AI 咨询 / 我的收藏）
├─ css/
│  └─ style.css
└─ js/
   ├─ api.js           # fetch 封装（统一携带 X-Device-Id、错误处理）
   ├─ utils.js         # 设备 ID 生成与读取
   ├─ app.js           # 页面初始化、导航切换
   ├─ food.js          # 美食列表/详情渲染
   ├─ attraction.js    # 景点列表/详情渲染
   ├─ ai.js            # AI 咨询交互
   └─ favorite.js      # 收藏操作与列表渲染
```

---

## 6. API 设计

**通用约定**：

- 基路径：`/api`
- 请求/响应均为 JSON。
- 收藏相关请求需携带请求头 `X-Device-Id`。
- 列表接口支持 `page`（默认 1）、`page_size`（默认 10，上限 100）、`keyword`（可选搜索）参数，返回统一分页结构：
  ```json
  { "items": [], "total": 100, "page": 1, "page_size": 10 }
  ```
- 统一错误结构：
  ```json
  { "detail": "错误描述" }
  ```

- **HTTP 状态码约定**：

  | 状态码 | 场景 |
  |--------|------|
  | 200 | 查询 / 详情 / 咨询成功 |
  | 201 | 收藏新增成功 |
  | 204 | 取消收藏成功（无返回体） |
  | 400 | 参数非法（target_type 非法、question 为空等） |
  | 404 | 目标不存在（美食 / 景点 / 收藏） |
  | 502 | DeepSeek 调用失败 / 超时 |

### 6.1 美食模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/foods` | 美食列表（分页 + 关键字搜索） |
| GET | `/api/foods/{id}` | 美食详情（含推荐门店列表） |

**GET `/api/foods/{id}` 响应示例**：

```json
{
  "id": 1,
  "name": "南昌拌粉",
  "description": "……",
  "avg_price": 12.0,
  "image_url": null,
  "stores": [
    { "id": 1, "name": "某某拌粉店", "address": "……" }
  ]
}
```

### 6.2 景点模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/attractions` | 景点列表（分页 + 关键字搜索） |
| GET | `/api/attractions/{id}` | 景点详情 |

### 6.3 AI 咨询模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/consult` | AI 游玩咨询（一次性返回） |

**请求体**：

```json
{ "question": "帮我规划一天南昌美食行程" }
```

**响应体**：

```json
{
  "answer": "根据南昌特色，建议……",
  "references": {
    "foods": [ { "id": 1, "name": "南昌拌粉", "avg_price": 12.0 } ],
    "attractions": [ { "id": 1, "name": "滕王阁", "ticket_price": "50 元" } ]
  }
}
```

### 6.4 收藏模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/favorites` | 我的收藏列表（分页，含对象详情） |
| POST | `/api/favorites` | 添加收藏 |
| DELETE | `/api/favorites/{target_type}/{target_id}` | 取消收藏 |
| GET | `/api/favorites/status?target_type=food&target_id=1` | 查询是否已收藏 |

**POST `/api/favorites` 请求体**：

```json
{ "target_type": "food", "target_id": 1 }
```

**GET `/api/favorites` 响应示例**：

```json
{
  "items": [
    { "target_type": "food", "target_id": 1, "food": { "id": 1, "name": "南昌拌粉", "avg_price": 12.0 } },
    { "target_type": "attraction", "target_id": 2, "attraction": { "id": 2, "name": "滕王阁", "ticket_price": "50 元" } }
  ],
  "total": 2,
  "page": 1,
  "page_size": 10
}
```

---

## 7. AI 咨询详细设计

### 7.1 处理流程

```
用户问题
   │
   ▼
service.ai.consult(question)
   ├─ 1. 实体匹配：遍历 food.name / attraction.name，若名称作为
   │     子串出现在问题中，则精确召回相关美食/景点
   ├─ 2. 兜底检索：步骤 1 无命中时，用问题关键词对 name/description
   │     做 LIKE 模糊匹配（Top 5）
   ├─ 3. 构建上下文：将命中的美食/景点序列化为精简 JSON
   ├─ 4. 组装 prompt：系统提示词 + 上下文 + 用户问题
   ├─ 5. 调用 DeepSeek（chat completion，一次性）
   └─ 6. 返回 { answer, references }
```

### 7.2 Prompt 结构

**系统提示词（角色设定）**：

> 你是「南昌旅游美食助手」，请基于提供的南昌本地美食与景点数据回答用户问题，给出实用的游玩/美食攻略建议。若数据不足以回答，请诚实说明，不要编造。

**上下文（注入数据）**：

```
以下为南昌本地数据：
【美食】
- 南昌拌粉：人均 12 元；简介……；推荐门店：……
【景点】
- 滕王阁：开放时间 08:00-18:00；门票 50 元；简介……
```

**用户问题**：原样透传。

### 7.3 关键点

- **检索策略**：优先「实体名反向匹配」（问题中包含某美食/景点名称即命中），无命中时退化为关键词 LIKE 模糊匹配（Top 5）；不引入分词库或向量检索/RAG，YAGNI。
- **DeepSeek 配置**从环境变量读取：`DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`（默认 `deepseek-chat`）。
- **异常处理**：DeepSeek 调用失败或超时，返回 `502` 及明确错误信息，前端展示友好提示；不影响美食/景点浏览。

---

## 8. 非功能需求

| 维度 | 要求 |
|------|------|
| 性能 | 列表接口 P95 响应 < 200ms；AI 咨询接口受 DeepSeek 制约，前端需有加载态与超时（建议 60s）处理 |
| 安全 | 无敏感数据；AI API Key 仅存后端环境变量，不暴露前端；SQL 使用参数化/ORM 防注入 |
| 兼容性 | 仅 PC 端，支持 Chrome / Edge / Firefox 最新两个大版本 |
| 可用性 | 无需登录，接口幂等（重复收藏不报错）；空数据展示空态 |
| 可维护性 | 后端分层清晰、一个模块一个包；全部 API 有单测；模块实现报告归档 |
| 成本 | AI 咨询接口做轻量限流（建议每设备每分钟 ≤ 5 次），控制 DeepSeek 调用成本；图片本地静态托管，无外链依赖 |

---

## 9. 测试策略

- **框架**：pytest + FastAPI `TestClient`。
- **数据库**：单测使用 SQLite 内存库（隔离），或对 repository 层 mock，避免依赖真实 MySQL。
- **AI 模块**：单测中 **mock DeepSeek 客户端**，不发起真实外部调用；校验 prompt 组装与上下文注入是否正确。
- **覆盖要求**：所有 API 端点均有单元测试，覆盖正常路径 + 主要异常路径（404 目标不存在、重复收藏、非法参数、AI 失败）。

| 模块 | 测试文件 | 关键用例 |
|------|----------|----------|
| 美食 | `tests/test_food.py` | 列表分页、搜索、详情含门店、404 |
| 景点 | `tests/test_attraction.py` | 列表分页、搜索、详情、404 |
| AI | `tests/test_ai.py` | 正常返回、上下文注入、DeepSeek 失败降级 |
| 收藏 | `tests/test_favorite.py` | 添加、列表、取消、重复收藏幂等、非法 target |

---

## 10. 文档输出（docs/implements）

每个模块完成后，在 `docs/implements/` 输出实现报告，说明模块职责、分层实现、接口清单与测试结果：

```
docs/implements/
├─ food.md           # 美食模块实现报告
├─ attraction.md     # 景点模块实现报告
├─ ai.md             # AI 咨询模块实现报告
└─ favorite.md       # 收藏模块实现报告
```

---

## 11. 里程碑与交付物

| 阶段 | 交付物 |
|------|--------|
| 1. 设计 | 本 PRD + 数据模型 + API 契约 |
| 2. 后端骨架 | FastAPI 项目结构、core 配置、数据库连接、种子数据 |
| 3. 模块实现 | food / attraction / ai / favorite 四模块（分层 + 单测 + 实现报告） |
| 4. 前端 | PC 端页面（首页、美食、景点、AI 咨询、我的收藏） |
| 5. 联调验收 | 前后端联调、全量测试通过、README 部署说明 |

---

## 12. 已确认设计决策

| 决策点 | 结论 |
|--------|------|
| AI 回答依据 | 注入本地美食/景点数据 |
| 收藏持久化 | 服务端按匿名设备标识（`X-Device-Id`） |
| 数据来源 | 预置种子数据，前端只读 |
| AI 响应方式 | 一次性返回 |
| 图片资源 | 真实图片，本地静态托管 |
| AI 检索策略 | 实体名反向匹配 + LIKE 兜底（Top 5） |
