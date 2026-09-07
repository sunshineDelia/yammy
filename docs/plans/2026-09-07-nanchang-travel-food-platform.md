# 南昌旅游美食推荐平台 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个面向游客的 PC 端南昌旅游美食推荐平台——美食/景点浏览、AI 攻略咨询、免登录收藏，后端 FastAPI 分层、前端原生三件套。

**Architecture:** 前端原生 HTML/CSS/JS 单页应用（`frontend/`），通过 REST 调用后端；后端 FastAPI 按 `router / service / repository` 三层、一个业务模块一个包（`food` / `attraction` / `ai` / `favorite`），SQLAlchemy 2.0 + MySQL（测试用 SQLite 内存库）；AI 调用 DeepSeek（注入本地数据、一次性返回）；收藏按匿名设备标识 `X-Device-Id` 持久化。

**Tech Stack:** Python 3.11+ / FastAPI / SQLAlchemy 2.0 / PyMySQL / Pydantic v2 / openai SDK(DeepSeek) / pytest + TestClient / 原生 HTML+CSS+JS

**Spec:** `d:\yammy\PRD.md`（本计划逐条实现该 PRD；执行者须同时阅读 PRD 与计划）

## Global Constraints

- 仅 PC 端，不做移动端/响应式适配（前端固定宽度 ~1100px 布局）。
- 前端原生 HTML + CSS + JavaScript，不引入任何框架/构建工具。
- 后端分层 router / service / repository；**一个模块一个包**（每模块自含 `model/schema/repository/service/router`）。
- 数据库 MySQL（生产）；**测试一律使用 SQLite 内存库**，不依赖真实 MySQL。
- AI 使用 DeepSeek：注入本地美食/景点数据、一次性返回；**测试必须 mock DeepSeek，禁止真实外呼**。
- 收藏持久化按匿名设备标识 `X-Device-Id`（UUID 存 localStorage，由前端生成）。
- 数据只读：美食/景点仅通过预置种子数据提供，无后台 CRUD。
- 图片为真实图，本地静态托管于 `backend/static/`。
- 所有 API 端点均有单元测试。
- 每个模块实现报告输出至 `docs/implements/`。
- 命名与响应结构严格遵循 PRD 第 6 节 API 契约（分页结构 `{items,total,page,page_size}`、错误结构 `{detail}`）。

---

## 文件结构总览

```
d:\yammy\
├─ PRD.md
├─ docs/
│  ├─ plans/          # 本计划
│  └─ implements/     # 模块实现报告（Task 9）
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ core/ (config.py, database.py, deps.py)
│  │  └─ modules/
│  │     ├─ food/ (model.py, schema.py, repository.py, service.py, router.py)
│  │     ├─ attraction/ (同 food 结构)
│  │     ├─ ai/ (schema.py, deepseek_client.py, context_builder.py, service.py, router.py)
│  │     └─ favorite/ (model.py, schema.py, repository.py, service.py, router.py)
│  ├─ static/images/{foods,attractions}/   # 真实图片
│  ├─ seed/seed.py
│  ├─ tests/ (conftest.py, test_food.py, test_attraction.py, test_favorite.py, test_ai.py)
│  ├─ requirements.txt
│  ├─ .env.example
│  └─ .gitignore
└─ frontend/
   ├─ index.html
   ├─ css/style.css
   └─ js/ (utils.js, api.js, food.js, attraction.js, ai.js, favorite.js, app.js)
```

---

## Task 1: 项目骨架 + 配置 + 数据库 + 健康检查

**Files:**
- Create: `backend/requirements.txt`, `backend/.env.example`, `backend/.gitignore`
- Create: `backend/app/__init__.py`, `backend/app/core/__init__.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/core/deps.py`, `backend/app/main.py`
- Create: `backend/tests/__init__.py`, `backend/tests/conftest.py`, `backend/tests/test_health.py`

**Interfaces:**
- Produces: `app.core.config.settings`（含 `database_url` / `deepseek_api_key` / `deepseek_base_url` / `deepseek_model`）、`app.core.database.Base` / `SessionLocal` / `engine`、`app.core.deps.get_db`、`app.main.app`（FastAPI 实例，含 `/api/health` 与 `/static` 挂载）。后续所有模块 `model` 继承 `Base`，`router` 依赖 `get_db`，`conftest` 依赖 `app` 与 `get_db`。

- [ ] **Step 1: 初始化 git 与目录**

```bash
cd /d/yammy && git init -b main
mkdir -p backend/app/core backend/app/modules backend/static/images/foods backend/static/images/attractions backend/seed backend/tests frontend/css frontend/js docs/implements docs/plans
```

- [ ] **Step 2: 写依赖与配置文件**

`backend/requirements.txt`：
```
fastapi
uvicorn[standard]
sqlalchemy
pymysql
cryptography
pydantic
pydantic-settings
openai
httpx
pytest
```

`backend/.env.example`：
```
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/nanchang_travel?charset=utf8mb4
DEEPSEEK_API_KEY=sk-xxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

`backend/.gitignore`：
```
__pycache__/
*.pyc
.venv/
venv/
.env
.pytest_cache/
```

- [ ] **Step 3: 写失败测试**

`backend/tests/test_health.py`：
```python
def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

`backend/tests/conftest.py`：
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.deps import get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

- [ ] **Step 4: 运行测试确认失败**

Run: `cd /d/yammy/backend && python -m pytest tests/test_health.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'app'`）

- [ ] **Step 5: 实现 core 与 main**

`backend/app/core/config.py`：
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "南昌旅游美食推荐平台"
    database_url: str = (
        "mysql+pymysql://root:password@localhost:3306/nanchang_travel?charset=utf8mb4"
    )
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"


settings = Settings()
```

`backend/app/core/database.py`：
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
```

`backend/app/core/deps.py`：
```python
from fastapi import Header, HTTPException

from app.core.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_device_id(x_device_id: str = Header("", alias="X-Device-Id")) -> str:
    if not x_device_id:
        raise HTTPException(status_code=400, detail="缺少 X-Device-Id 请求头")
    return x_device_id
```

`backend/app/main.py`：
```python
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: 运行测试确认通过**

Run: `cd /d/yammy/backend && python -m pytest tests/test_health.py -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
cd /d/yammy && git add backend && git commit -m "chore: 项目骨架 + 配置 + 数据库 + 健康检查"
```

---

## Task 2: 美食模块（food）

**Files:**
- Create: `backend/app/modules/food/__init__.py`, `backend/app/modules/food/model.py`, `backend/app/modules/food/schema.py`, `backend/app/modules/food/repository.py`, `backend/app/modules/food/service.py`, `backend/app/modules/food/router.py`
- Modify: `backend/app/main.py`（注册 food 路由）
- Test: `backend/tests/test_food.py`

**Interfaces:**
- Consumes: `Base`、`Session`、`get_db`
- Produces: `Food`（含 `stores` relationship）、`Store`、`FoodOut` / `FoodListOut` / `FoodBrief`、`FoodRepository.list/get_by_id/list_all/search`、`FoodService.list_foods/get_food`。后续 `ai` 模块的 `context_builder` 依赖 `FoodRepository.list_all/search` 与 `FoodBrief`；`favorite` 模块依赖 `FoodRepository.get_by_id` 与 `FoodBrief`。

- [ ] **Step 1: 写失败测试**

`backend/tests/test_food.py`：
```python
from app.modules.food.model import Food, Store


def _seed(db):
    f1 = Food(name="南昌拌粉", description="南昌最具代表性的小吃", avg_price=12.0)
    f1.stores = [Store(name="黄记拌粉", address="中山路1号")]
    f2 = Food(name="瓦罐汤", description="南昌传统煨汤", avg_price=20.0)
    db.add_all([f1, f2])
    db.commit()
    for f in (f1, f2):
        db.refresh(f)
    return f1, f2


def test_list_foods(client, db_session):
    _seed(db_session)
    resp = client.get("/api/foods")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_list_foods_search(client, db_session):
    _seed(db_session)
    resp = client.get("/api/foods", params={"keyword": "瓦罐"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "瓦罐汤"


def test_get_food_detail_with_stores(client, db_session):
    f1, _ = _seed(db_session)
    resp = client.get(f"/api/foods/{f1.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "南昌拌粉"
    assert data["stores"][0]["name"] == "黄记拌粉"


def test_get_food_not_found(client, db_session):
    resp = client.get("/api/foods/999")
    assert resp.status_code == 404
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /d/yammy/backend && python -m pytest tests/test_food.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'app.modules.food'`）

- [ ] **Step 3: 实现 model 与 schema**

`backend/app/modules/food/model.py`：
```python
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Food(Base):
    __tablename__ = "food"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    avg_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    stores: Mapped[list["Store"]] = relationship(
        back_populates="food", cascade="all, delete-orphan"
    )


class Store(Base):
    __tablename__ = "store"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    food_id: Mapped[int] = mapped_column(ForeignKey("food.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    food: Mapped["Food"] = relationship(back_populates="stores")
```

`backend/app/modules/food/schema.py`：
```python
from pydantic import BaseModel, ConfigDict


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str | None = None


class FoodBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    avg_price: float
    image_url: str | None = None


class FoodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    avg_price: float
    image_url: str | None = None
    stores: list[StoreOut] = []


class FoodListOut(BaseModel):
    items: list[FoodOut]
    total: int
    page: int
    page_size: int
```

- [ ] **Step 4: 实现 repository / service / router 并注册**

`backend/app/modules/food/repository.py`：
```python
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.food.model import Food


class FoodRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, page: int, page_size: int, keyword: str | None = None) -> tuple[list[Food], int]:
        stmt = select(Food)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Food.name.like(like), Food.description.like(like)))
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.options(selectinload(Food.stores))
                .order_by(Food.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def get_by_id(self, food_id: int) -> Food | None:
        stmt = select(Food).options(selectinload(Food.stores)).where(Food.id == food_id)
        return self.db.scalar(stmt)

    def list_all(self) -> list[Food]:
        return list(self.db.scalars(select(Food).options(selectinload(Food.stores))))

    def search(self, keyword: str, limit: int = 5) -> list[Food]:
        like = f"%{keyword}%"
        stmt = (
            select(Food)
            .options(selectinload(Food.stores))
            .where(or_(Food.name.like(like), Food.description.like(like)))
            .limit(limit)
        )
        return list(self.db.scalars(stmt))
```

`backend/app/modules/food/service.py`：
```python
from app.modules.food.repository import FoodRepository
from app.modules.food.schema import FoodListOut, FoodOut


class FoodService:
    def __init__(self, repo: FoodRepository):
        self.repo = repo

    def list_foods(self, page: int, page_size: int, keyword: str | None = None) -> FoodListOut:
        items, total = self.repo.list(page, page_size, keyword)
        return FoodListOut(
            items=[FoodOut.model_validate(f) for f in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_food(self, food_id: int) -> FoodOut | None:
        food = self.repo.get_by_id(food_id)
        return FoodOut.model_validate(food) if food else None
```

`backend/app/modules/food/router.py`：
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.modules.food.repository import FoodRepository
from app.modules.food.schema import FoodListOut, FoodOut
from app.modules.food.service import FoodService

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("", response_model=FoodListOut)
def list_foods(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = None,
    db: Session = Depends(get_db),
):
    return FoodService(FoodRepository(db)).list_foods(page, page_size, keyword)


@router.get("/{food_id}", response_model=FoodOut)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = FoodService(FoodRepository(db)).get_food(food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="美食不存在")
    return food
```

在 `backend/app/main.py` 中新增：
```python
from app.modules.food.router import router as food_router
# 在 app.mount(...) 之后：
app.include_router(food_router, prefix="/api")
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd /d/yammy/backend && python -m pytest tests/test_food.py -v`
Expected: PASS（4 passed）

- [ ] **Step 6: 提交**

```bash
cd /d/yammy && git add backend && git commit -m "feat: 美食模块（列表/详情/搜索）"
```

---

## Task 3: 景点模块（attraction）

**Files:**
- Create: `backend/app/modules/attraction/__init__.py`, `backend/app/modules/attraction/model.py`, `backend/app/modules/attraction/schema.py`, `backend/app/modules/attraction/repository.py`, `backend/app/modules/attraction/service.py`, `backend/app/modules/attraction/router.py`
- Modify: `backend/app/main.py`（注册 attraction 路由）
- Test: `backend/tests/test_attraction.py`

**Interfaces:**
- Consumes: `Base`、`Session`、`get_db`
- Produces: `Attraction`、`AttractionOut` / `AttractionListOut` / `AttractionBrief`、`AttractionRepository.list/get_by_id/list_all/search`。后续 `ai` 与 `favorite` 模块依赖 `AttractionRepository.get_by_id/list_all/search` 与 `AttractionBrief`。

- [ ] **Step 1: 写失败测试**

`backend/tests/test_attraction.py`：
```python
from app.modules.attraction.model import Attraction


def _seed(db):
    a1 = Attraction(name="滕王阁", description="江南三大名楼之一", open_time="08:00-18:00", ticket_price="50 元")
    a2 = Attraction(name="八一广场", description="南昌城市中心广场", open_time="全天开放", ticket_price="免费")
    db.add_all([a1, a2])
    db.commit()
    for a in (a1, a2):
        db.refresh(a)
    return a1, a2


def test_list_attractions(client, db_session):
    _seed(db_session)
    resp = client.get("/api/attractions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_attractions_search(client, db_session):
    _seed(db_session)
    resp = client.get("/api/attractions", params={"keyword": "滕王阁"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "滕王阁"


def test_get_attraction_detail(client, db_session):
    a1, _ = _seed(db_session)
    resp = client.get(f"/api/attractions/{a1.id}")
    assert resp.status_code == 200
    assert resp.json()["ticket_price"] == "50 元"


def test_get_attraction_not_found(client, db_session):
    resp = client.get("/api/attractions/999")
    assert resp.status_code == 404
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /d/yammy/backend && python -m pytest tests/test_attraction.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'app.modules.attraction'`）

- [ ] **Step 3: 实现 model / schema / repository / service / router**

`backend/app/modules/attraction/model.py`：
```python
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Attraction(Base):
    __tablename__ = "attraction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    open_time: Mapped[str] = mapped_column(String(100), nullable=False)
    ticket_price: Mapped[str] = mapped_column(String(100), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
```

`backend/app/modules/attraction/schema.py`：
```python
from pydantic import BaseModel, ConfigDict


class AttractionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ticket_price: str
    image_url: str | None = None


class AttractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    open_time: str
    ticket_price: str
    image_url: str | None = None


class AttractionListOut(BaseModel):
    items: list[AttractionOut]
    total: int
    page: int
    page_size: int
```

`backend/app/modules/attraction/repository.py`：
```python
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.attraction.model import Attraction


class AttractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, page: int, page_size: int, keyword: str | None = None) -> tuple[list[Attraction], int]:
        stmt = select(Attraction)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Attraction.name.like(like), Attraction.description.like(like)))
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Attraction.id).offset((page - 1) * page_size).limit(page_size)
            )
        )
        return items, total

    def get_by_id(self, attraction_id: int) -> Attraction | None:
        return self.db.scalar(select(Attraction).where(Attraction.id == attraction_id))

    def list_all(self) -> list[Attraction]:
        return list(self.db.scalars(select(Attraction)))

    def search(self, keyword: str, limit: int = 5) -> list[Attraction]:
        like = f"%{keyword}%"
        stmt = (
            select(Attraction)
            .where(or_(Attraction.name.like(like), Attraction.description.like(like)))
            .limit(limit)
        )
        return list(self.db.scalars(stmt))
```

`backend/app/modules/attraction/service.py`：
```python
from app.modules.attraction.repository import AttractionRepository
from app.modules.attraction.schema import AttractionListOut, AttractionOut


class AttractionService:
    def __init__(self, repo: AttractionRepository):
        self.repo = repo

    def list_attractions(self, page: int, page_size: int, keyword: str | None = None) -> AttractionListOut:
        items, total = self.repo.list(page, page_size, keyword)
        return AttractionListOut(
            items=[AttractionOut.model_validate(a) for a in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_attraction(self, attraction_id: int) -> AttractionOut | None:
        attraction = self.repo.get_by_id(attraction_id)
        return AttractionOut.model_validate(attraction) if attraction else None
```

`backend/app/modules/attraction/router.py`：
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.modules.attraction.repository import AttractionRepository
from app.modules.attraction.schema import AttractionListOut, AttractionOut
from app.modules.attraction.service import AttractionService

router = APIRouter(prefix="/attractions", tags=["attractions"])


@router.get("", response_model=AttractionListOut)
def list_attractions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = None,
    db: Session = Depends(get_db),
):
    return AttractionService(AttractionRepository(db)).list_attractions(page, page_size, keyword)


@router.get("/{attraction_id}", response_model=AttractionOut)
def get_attraction(attraction_id: int, db: Session = Depends(get_db)):
    attraction = AttractionService(AttractionRepository(db)).get_attraction(attraction_id)
    if attraction is None:
        raise HTTPException(status_code=404, detail="景点不存在")
    return attraction
```

在 `backend/app/main.py` 中新增：
```python
from app.modules.attraction.router import router as attraction_router
# ...
app.include_router(attraction_router, prefix="/api")
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /d/yammy/backend && python -m pytest tests/test_attraction.py -v`
Expected: PASS（4 passed）

- [ ] **Step 5: 提交**

```bash
cd /d/yammy && git add backend && git commit -m "feat: 景点模块（列表/详情/搜索）"
```

---

## Task 4: 收藏模块（favorite）

**Files:**
- Create: `backend/app/modules/favorite/__init__.py`, `backend/app/modules/favorite/model.py`, `backend/app/modules/favorite/schema.py`, `backend/app/modules/favorite/repository.py`, `backend/app/modules/favorite/service.py`, `backend/app/modules/favorite/router.py`
- Modify: `backend/app/main.py`（注册 favorite 路由）
- Test: `backend/tests/test_favorite.py`

**Interfaces:**
- Consumes: `get_db`、`get_device_id`（`app.core.deps`）、`FoodRepository.get_by_id`、`AttractionRepository.get_by_id`、`FoodBrief`、`AttractionBrief`
- Produces: `Favorite`、`FavoriteService.add/remove/status/list_favorites`；后续无模块依赖 favorite。

- [ ] **Step 1: 写失败测试**

`backend/tests/test_favorite.py`：
```python
from app.modules.food.model import Food


def _seed_food(db):
    f = Food(name="南昌拌粉", description="南昌特色小吃", avg_price=12.0)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def test_add_favorite(client, db_session):
    f = _seed_food(db_session)
    resp = client.post(
        "/api/favorites",
        json={"target_type": "food", "target_id": f.id},
        headers={"X-Device-Id": "dev1"},
    )
    assert resp.status_code == 201


def test_add_favorite_idempotent(client, db_session):
    f = _seed_food(db_session)
    h = {"X-Device-Id": "dev1"}
    client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers=h)
    resp = client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers=h)
    assert resp.status_code == 200


def test_add_favorite_invalid_type(client, db_session):
    resp = client.post(
        "/api/favorites",
        json={"target_type": "foo", "target_id": 1},
        headers={"X-Device-Id": "dev1"},
    )
    assert resp.status_code == 400


def test_add_favorite_target_not_found(client, db_session):
    resp = client.post(
        "/api/favorites",
        json={"target_type": "food", "target_id": 999},
        headers={"X-Device-Id": "dev1"},
    )
    assert resp.status_code == 404


def test_missing_device_id(client, db_session):
    resp = client.post("/api/favorites", json={"target_type": "food", "target_id": 1})
    assert resp.status_code == 400


def test_list_favorites_with_detail(client, db_session):
    f = _seed_food(db_session)
    client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers={"X-Device-Id": "dev1"})
    resp = client.get("/api/favorites", headers={"X-Device-Id": "dev1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["food"]["name"] == "南昌拌粉"


def test_delete_favorite(client, db_session):
    f = _seed_food(db_session)
    client.post("/api/favorites", json={"target_type": "food", "target_id": f.id}, headers={"X-Device-Id": "dev1"})
    resp = client.delete(f"/api/favorites/food/{f.id}", headers={"X-Device-Id": "dev1"})
    assert resp.status_code == 204


def test_status(client, db_session):
    f = _seed_food(db_session)
    resp = client.get("/api/favorites/status", params={"target_type": "food", "target_id": f.id}, headers={"X-Device-Id": "dev1"})
    assert resp.json() == {"favorited": False}
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /d/yammy/backend && python -m pytest tests/test_favorite.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'app.modules.favorite'`）

- [ ] **Step 3: 实现 model / schema / repository**

`backend/app/modules/favorite/model.py`：
```python
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorite"
    __table_args__ = (
        UniqueConstraint("device_id", "target_type", "target_id", name="uq_favorite"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
```

`backend/app/modules/favorite/schema.py`：
```python
from datetime import datetime

from pydantic import BaseModel

from app.modules.attraction.schema import AttractionBrief
from app.modules.food.schema import FoodBrief


class FavoriteCreate(BaseModel):
    target_type: str
    target_id: int


class FavoriteItem(BaseModel):
    target_type: str
    target_id: int
    created_at: datetime
    food: FoodBrief | None = None
    attraction: AttractionBrief | None = None


class FavoriteListOut(BaseModel):
    items: list[FavoriteItem]
    total: int
    page: int
    page_size: int


class FavoriteStatus(BaseModel):
    favorited: bool
```

`backend/app/modules/favorite/repository.py`：
```python
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.favorite.model import Favorite


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, device_id: str, target_type: str, target_id: int) -> Favorite | None:
        return self.db.scalar(
            select(Favorite).where(
                Favorite.device_id == device_id,
                Favorite.target_type == target_type,
                Favorite.target_id == target_id,
            )
        )

    def add(self, device_id: str, target_type: str, target_id: int) -> Favorite:
        fav = Favorite(device_id=device_id, target_type=target_type, target_id=target_id)
        self.db.add(fav)
        self.db.commit()
        self.db.refresh(fav)
        return fav

    def delete(self, device_id: str, target_type: str, target_id: int) -> bool:
        fav = self.get(device_id, target_type, target_id)
        if fav is None:
            return False
        self.db.delete(fav)
        self.db.commit()
        return True

    def list(self, device_id: str, page: int, page_size: int) -> tuple[list[Favorite], int]:
        stmt = select(Favorite).where(Favorite.device_id == device_id)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Favorite.id.desc()).offset((page - 1) * page_size).limit(page_size)
            )
        )
        return items, total
```

- [ ] **Step 4: 实现 service 与 router 并注册**

`backend/app/modules/favorite/service.py`：
```python
from fastapi import HTTPException

from app.modules.attraction.repository import AttractionRepository
from app.modules.attraction.schema import AttractionBrief
from app.modules.favorite.model import Favorite
from app.modules.favorite.repository import FavoriteRepository
from app.modules.favorite.schema import FavoriteItem, FavoriteListOut, FavoriteStatus
from app.modules.food.repository import FoodRepository
from app.modules.food.schema import FoodBrief

VALID_TARGET_TYPES = ("food", "attraction")


class FavoriteService:
    def __init__(
        self,
        repo: FavoriteRepository,
        food_repo: FoodRepository,
        attraction_repo: AttractionRepository,
    ):
        self.repo = repo
        self.food_repo = food_repo
        self.attraction_repo = attraction_repo

    def _target_exists(self, target_type: str, target_id: int) -> bool:
        if target_type == "food":
            return self.food_repo.get_by_id(target_id) is not None
        if target_type == "attraction":
            return self.attraction_repo.get_by_id(target_id) is not None
        return False

    def add(self, device_id: str, target_type: str, target_id: int) -> tuple[Favorite, bool]:
        if target_type not in VALID_TARGET_TYPES:
            raise HTTPException(status_code=400, detail="target_type 非法")
        if not self._target_exists(target_type, target_id):
            raise HTTPException(status_code=404, detail="收藏对象不存在")
        existing = self.repo.get(device_id, target_type, target_id)
        if existing is not None:
            return existing, False
        return self.repo.add(device_id, target_type, target_id), True

    def remove(self, device_id: str, target_type: str, target_id: int) -> bool:
        return self.repo.delete(device_id, target_type, target_id)

    def status(self, device_id: str, target_type: str, target_id: int) -> FavoriteStatus:
        return FavoriteStatus(favorited=self.repo.get(device_id, target_type, target_id) is not None)

    def list_favorites(self, device_id: str, page: int, page_size: int) -> FavoriteListOut:
        items, total = self.repo.list(device_id, page, page_size)
        result = []
        for fav in items:
            item = FavoriteItem(
                target_type=fav.target_type,
                target_id=fav.target_id,
                created_at=fav.created_at,
            )
            if fav.target_type == "food":
                food = self.food_repo.get_by_id(fav.target_id)
                if food is not None:
                    item.food = FoodBrief.model_validate(food)
            elif fav.target_type == "attraction":
                attraction = self.attraction_repo.get_by_id(fav.target_id)
                if attraction is not None:
                    item.attraction = AttractionBrief.model_validate(attraction)
            result.append(item)
        return FavoriteListOut(items=result, total=total, page=page, page_size=page_size)
```

`backend/app/modules/favorite/router.py`：
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_device_id
from app.modules.attraction.repository import AttractionRepository
from app.modules.favorite.repository import FavoriteRepository
from app.modules.favorite.schema import FavoriteCreate, FavoriteListOut, FavoriteStatus
from app.modules.favorite.service import FavoriteService
from app.modules.food.repository import FoodRepository

router = APIRouter(prefix="/favorites", tags=["favorites"])


def _service(db: Session) -> FavoriteService:
    return FavoriteService(FavoriteRepository(db), FoodRepository(db), AttractionRepository(db))


@router.get("", response_model=FavoriteListOut)
def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    return _service(db).list_favorites(device_id, page, page_size)


@router.post("")
def add_favorite(
    payload: FavoriteCreate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    fav, created = _service(db).add(device_id, payload.target_type, payload.target_id)
    return JSONResponse(
        status_code=201 if created else 200,
        content={"target_type": fav.target_type, "target_id": fav.target_id},
    )


@router.delete("/{target_type}/{target_id}", status_code=204)
def remove_favorite(
    target_type: str,
    target_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    if not _service(db).remove(device_id, target_type, target_id):
        raise HTTPException(status_code=404, detail="收藏不存在")
    return Response(status_code=204)


@router.get("/status", response_model=FavoriteStatus)
def favorite_status(
    target_type: str,
    target_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    return _service(db).status(device_id, target_type, target_id)
```

在 `backend/app/main.py` 中新增：
```python
from app.modules.favorite.router import router as favorite_router
# ...
app.include_router(favorite_router, prefix="/api")
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd /d/yammy/backend && python -m pytest tests/test_favorite.py -v`
Expected: PASS（8 passed）

- [ ] **Step 6: 提交**

```bash
cd /d/yammy && git add backend && git commit -m "feat: 收藏模块（增删查/状态/幂等）"
```

---

## Task 5: AI 咨询模块（ai）

**Files:**
- Create: `backend/app/modules/ai/__init__.py`, `backend/app/modules/ai/schema.py`, `backend/app/modules/ai/deepseek_client.py`, `backend/app/modules/ai/context_builder.py`, `backend/app/modules/ai/service.py`, `backend/app/modules/ai/router.py`
- Modify: `backend/app/main.py`（注册 ai 路由）
- Test: `backend/tests/test_ai.py`

**Interfaces:**
- Consumes: `settings`（DeepSeek 配置）、`FoodRepository.list_all/search`、`AttractionRepository.list_all/search`、`FoodBrief`、`AttractionBrief`
- Produces: `DeepSeekClient.chat(messages) -> str`（懒初始化 OpenAI 客户端）、`ContextBuilder.retrieve/build_messages`、`AIService.consult(question) -> ConsultResponse`。测试通过 `patch.object(DeepSeekClient, "chat", ...)` 打桩，不真实外呼。

- [ ] **Step 1: 写失败测试**

`backend/tests/test_ai.py`：
```python
from unittest.mock import patch

from app.modules.ai.deepseek_client import DeepSeekClient
from app.modules.food.model import Food


def _seed(db):
    f = Food(name="南昌拌粉", description="南昌特色小吃", avg_price=12.0)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def test_consult_returns_answer_and_reference(client, db_session):
    _seed(db_session)
    with patch.object(DeepSeekClient, "chat", return_value="建议你去吃南昌拌粉"):
        resp = client.post("/api/ai/consult", json={"question": "南昌拌粉在哪里吃"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "建议你去吃南昌拌粉"
    assert data["references"]["foods"][0]["name"] == "南昌拌粉"


def test_consult_injects_local_context(client, db_session):
    _seed(db_session)
    captured = {}

    def fake_chat(self, messages):
        captured["messages"] = messages
        return "ok"

    with patch.object(DeepSeekClient, "chat", fake_chat):
        client.post("/api/ai/consult", json={"question": "南昌拌粉怎么样"})
    assert "【美食】" in captured["messages"][1]["content"]


def test_consult_empty_question(client, db_session):
    resp = client.post("/api/ai/consult", json={"question": ""})
    assert resp.status_code == 422


def test_consult_deepseek_failure(client, db_session):
    with patch.object(DeepSeekClient, "chat", side_effect=Exception("boom")):
        resp = client.post("/api/ai/consult", json={"question": "test"})
    assert resp.status_code == 502
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /d/yammy/backend && python -m pytest tests/test_ai.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'app.modules.ai'`）

- [ ] **Step 3: 实现 schema / deepseek_client / context_builder**

`backend/app/modules/ai/schema.py`：
```python
from pydantic import BaseModel, Field

from app.modules.attraction.schema import AttractionBrief
from app.modules.food.schema import FoodBrief


class ConsultRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class ConsultReferences(BaseModel):
    foods: list[FoodBrief]
    attractions: list[AttractionBrief]


class ConsultResponse(BaseModel):
    answer: str
    references: ConsultReferences
```

`backend/app/modules/ai/deepseek_client.py`：
```python
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
```

`backend/app/modules/ai/context_builder.py`：
```python
from app.modules.attraction.repository import AttractionRepository
from app.modules.food.repository import FoodRepository

SYSTEM_PROMPT = (
    "你是「南昌旅游美食助手」，请基于提供的南昌本地美食与景点数据回答用户问题，"
    "给出实用的游玩/美食攻略建议。若数据不足以回答，请诚实说明，不要编造。"
)


class ContextBuilder:
    def __init__(self, food_repo: FoodRepository, attraction_repo: AttractionRepository):
        self.food_repo = food_repo
        self.attraction_repo = attraction_repo

    def retrieve(self, question: str) -> dict:
        foods = [f for f in self.food_repo.list_all() if f.name and f.name in question]
        attractions = [a for a in self.attraction_repo.list_all() if a.name and a.name in question]
        if not foods and not attractions:
            foods = self.food_repo.search(question, limit=5)
            attractions = self.attraction_repo.search(question, limit=5)
        return {"foods": foods[:5], "attractions": attractions[:5]}

    def _format_context(self, context: dict) -> str:
        lines = ["以下为南昌本地数据：", "【美食】"]
        for f in context["foods"]:
            stores = "、".join(s.name for s in f.stores)
            lines.append(f"- {f.name}：人均 {f.avg_price} 元；{f.description}；推荐门店：{stores}")
        lines.append("【景点】")
        for a in context["attractions"]:
            lines.append(f"- {a.name}：开放时间 {a.open_time}；门票 {a.ticket_price}；{a.description}")
        return "\n".join(lines)

    def build_messages(self, question: str, context: dict) -> list[dict]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{self._format_context(context)}\n\n用户问题：{question}"},
        ]
```

- [ ] **Step 4: 实现 service 与 router 并注册**

`backend/app/modules/ai/service.py`：
```python
from app.modules.ai.context_builder import ContextBuilder
from app.modules.ai.deepseek_client import DeepSeekClient
from app.modules.ai.schema import ConsultReferences, ConsultResponse
from app.modules.attraction.schema import AttractionBrief
from app.modules.food.schema import FoodBrief


class AIService:
    def __init__(self, context_builder: ContextBuilder, client: DeepSeekClient):
        self.context_builder = context_builder
        self.client = client

    def consult(self, question: str) -> ConsultResponse:
        context = self.context_builder.retrieve(question)
        messages = self.context_builder.build_messages(question, context)
        answer = self.client.chat(messages)
        return ConsultResponse(
            answer=answer,
            references=ConsultReferences(
                foods=[FoodBrief.model_validate(f) for f in context["foods"]],
                attractions=[AttractionBrief.model_validate(a) for a in context["attractions"]],
            ),
        )
```

`backend/app/modules/ai/router.py`：
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.modules.ai.context_builder import ContextBuilder
from app.modules.ai.deepseek_client import DeepSeekClient
from app.modules.ai.schema import ConsultRequest, ConsultResponse
from app.modules.ai.service import AIService
from app.modules.attraction.repository import AttractionRepository
from app.modules.food.repository import FoodRepository

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/consult", response_model=ConsultResponse)
def consult(payload: ConsultRequest, db: Session = Depends(get_db)):
    service = AIService(
        ContextBuilder(FoodRepository(db), AttractionRepository(db)),
        DeepSeekClient(),
    )
    try:
        return service.consult(payload.question)
    except Exception:
        raise HTTPException(status_code=502, detail="AI 服务调用失败")
```

在 `backend/app/main.py` 中新增：
```python
from app.modules.ai.router import router as ai_router
# ...
app.include_router(ai_router, prefix="/api")
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd /d/yammy/backend && python -m pytest tests/test_ai.py -v`
Expected: PASS（4 passed）

- [ ] **Step 6: 提交**

```bash
cd /d/yammy && git add backend && git commit -m "feat: AI 咨询模块（DeepSeek 注入本地数据）"
```

---

## Task 6: 种子数据 + 静态图片

**Files:**
- Create: `backend/seed/__init__.py`, `backend/seed/seed.py`
- Create: `backend/static/images/README.md`
- Test: 无（人工验证脚本执行 + 首页接口有数据）

**Interfaces:**
- Consumes: `Base`、`SessionLocal`、`engine`、`Food`、`Store`、`Attraction`
- Produces: 6 条美食（含门店）+ 6 条景点数据，`image_url` 指向 `/static/images/...`；真实图片文件由用户/执行者放置到对应路径。

- [ ] **Step 1: 写种子脚本**

`backend/seed/seed.py`：
```python
"""预置种子数据。运行：cd backend && python -m seed.seed"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, SessionLocal, engine
from app.modules.attraction.model import Attraction
from app.modules.food.model import Food, Store


def seed() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.query(Food).count() > 0:
            print("检测到已有数据，跳过种子。")
            return

        foods = [
            Food(
                name="南昌拌粉", description="南昌最具代表性的小吃，米粉爽滑筋道，配花生米、萝卜干、辣椒油拌匀，酸辣开胃。",
                avg_price=12.0, image_url="/static/images/foods/nanchang_banfen.jpg",
                stores=[Store(name="黄记瓦罐拌粉", address="中山路"), Store(name="老南昌拌粉店", address="胜利路")],
            ),
            Food(
                name="瓦罐汤", description="用瓦罐煨制数小时的传统汤品，汤鲜味浓、滋补养胃，是南昌人早餐的经典搭配。",
                avg_price=20.0, image_url="/static/images/foods/waguan_tang.jpg",
                stores=[Store(name="民间瓦罐煨汤", address="八一广场")],
            ),
            Food(
                name="藜蒿炒腊肉", description="南昌名菜，藜蒿清香脆嫩，与腊肉同炒咸香下饭，是鄱阳湖一带的特色风味。",
                avg_price=35.0, image_url="/static/images/foods/lihao_chaolarou.jpg",
                stores=[Store(name="豫章人家", address="绳金塔")],
            ),
            Food(
                name="南昌白糖糕", description="传统甜点，糯米外裹糖霜，软糯香甜，是南昌人记忆里的童年味道。",
                avg_price=8.0, image_url="/static/images/foods/baitang_gao.jpg",
                stores=[Store(name="老字号白糖糕", address="孺子路")],
            ),
            Food(
                name="牛杂粉", description="粉滑汤浓，牛杂软烂入味，是南昌街头巷尾广受欢迎的平价美食。",
                avg_price=15.0, image_url="/static/images/foods/niuza_fen.jpg",
                stores=[Store(name="孺子路牛杂粉", address="孺子路")],
            ),
            Food(
                name="豫章酥鸭", description="南昌传统名菜，鸭肉酥烂脱骨，皮脆肉嫩，风味独特。",
                avg_price=55.0, image_url="/static/images/foods/yuzhang_suya.jpg",
                stores=[Store(name="豫章酒家", address="东湖区")],
            ),
        ]

        attractions = [
            Attraction(name="滕王阁", description="江南三大名楼之一，因王勃《滕王阁序》名扬天下，登楼可眺赣江风光。", open_time="08:00-18:00", ticket_price="50 元", image_url="/static/images/attractions/tengwangge.jpg"),
            Attraction(name="八一广场", description="南昌城市中心广场，江西重要的纪念性地标，夜景灯光尤为壮观。", open_time="全天开放", ticket_price="免费", image_url="/static/images/attractions/bayi_guangchang.jpg"),
            Attraction(name="绳金塔", description="南昌古塔之一，始建于唐代，周边汇聚地道南昌小吃，是美食爱好者的必去之地。", open_time="08:30-17:30", ticket_price="免费（登塔另收费）", image_url="/static/images/attractions/shengjin_ta.jpg"),
            Attraction(name="南昌之星摩天轮", description="世界较高的摩天轮之一，可俯瞰南昌城市与赣江全景，夜晚灯光璀璨。", open_time="09:30-22:00", ticket_price="50 元", image_url="/static/images/attractions/nanchang_zhixing.jpg"),
            Attraction(name="梅岭国家森林公园", description="南昌近郊的天然氧吧，四季景色各异，适合登山徒步与休闲度假。", open_time="全天开放", ticket_price="免费", image_url="/static/images/attractions/meiling.jpg"),
            Attraction(name="南昌汉代海昏侯国遗址公园", description="西汉海昏侯刘贺墓所在地，出土大量珍贵文物，是了解汉代历史的重要遗址。", open_time="09:00-17:00", ticket_price="60 元", image_url="/static/images/attractions/haihunhou.jpg"),
        ]

        db.add_all(foods + attractions)
        db.commit()
        print(f"种子数据完成：{len(foods)} 条美食，{len(attractions)} 条景点。")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
```

- [ ] **Step 2: 写图片说明（真实图须放置到对应路径）**

`backend/static/images/README.md`：
```markdown
# 图片资源（真实图）

种子数据引用的图片路径如下，请将**真实图片**（jpg/png，建议宽 800px 以上）放到对应文件名：

美食（`foods/`）：`nanchang_banfen.jpg`、`waguan_tang.jpg`、`lihao_chaolarou.jpg`、`baitang_gao.jpg`、`niuza_fen.jpg`、`yuzhang_suya.jpg`

景点（`attractions/`）：`tengwangge.jpg`、`bayi_guangchang.jpg`、`shengjin_ta.jpg`、`nanchang_zhixing.jpg`、`meiling.jpg`、`haihunhou.jpg`

图片来源：用户提供，或从可商用免费图库（Unsplash / Pexels）下载，禁止使用未授权图片。
```

- [ ] **Step 3: 建库并跑种子（人工验证）**

```bash
# 1) 建数据库（MySQL，一次性）
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS nanchang_travel CHARACTER SET utf8mb4;"
# 2) 配置 .env（复制 .env.example 并填写 DATABASE_URL / DEEPSEEK_API_KEY）
# 3) 安装依赖（首次）
cd /d/yammy/backend && python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt
# 4) 跑种子
python -m seed.seed
```
Expected: 输出「种子数据完成：6 条美食，6 条景点。」

- [ ] **Step 4: 提交**

```bash
cd /d/yammy && git add backend/seed backend/static && git commit -m "feat: 预置种子数据 + 静态图片目录"
```

---

## Task 7: 前端骨架（HTML / CSS / 通用 JS）

**Files:**
- Create: `frontend/index.html`, `frontend/css/style.css`
- Create: `frontend/js/utils.js`, `frontend/js/api.js`, `frontend/js/app.js`
- Test: 无自动化测试（人工浏览器验证）；约束仅要求后端 API 单测。

**Interfaces:**
- Produces: 全局 `getDeviceId()`、全局 `api`（`get/post/del`）、全局 `App`（视图路由与导航绑定）。后续 `food.js` / `attraction.js` / `ai.js` / `favorite.js` 依赖 `api` 与 DOM 容器约定（`<main id="view">` 内容区）。

- [ ] **Step 1: 写 index.html**

`frontend/index.html`：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>南昌旅游美食推荐平台</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="#/">南昌·游</a>
      <nav class="nav">
        <a href="#/foods" data-view="foods">美食</a>
        <a href="#/attractions" data-view="attractions">景点</a>
        <a href="#/ai" data-view="ai">AI 咨询</a>
        <a href="#/favorites" data-view="favorites">我的收藏</a>
      </nav>
    </div>
  </header>
  <main id="view" class="container"></main>
  <footer class="footer">南昌旅游美食推荐平台 · 仅供学习演示</footer>

  <script src="js/utils.js"></script>
  <script src="js/api.js"></script>
  <script src="js/food.js"></script>
  <script src="js/attraction.js"></script>
  <script src="js/ai.js"></script>
  <script src="js/favorite.js"></script>
  <script src="js/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: 写 style.css**

`frontend/css/style.css`：
```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; color: #333; background: #f6f7f9; min-height: 100vh; display: flex; flex-direction: column; }
.topbar { background: #b45309; color: #fff; }
.topbar-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; height: 56px; }
.brand { color: #fff; font-size: 20px; font-weight: 700; text-decoration: none; }
.nav a { color: #fff; text-decoration: none; margin-left: 24px; opacity: .85; }
.nav a.active, .nav a:hover { opacity: 1; }
.container { max-width: 1100px; width: 100%; margin: 24px auto; padding: 0 20px; flex: 1; }
.footer { text-align: center; color: #999; font-size: 12px; padding: 16px; }
.card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.card { background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.card img { width: 100%; height: 160px; object-fit: cover; background: #eee; display: block; }
.card-body { padding: 14px; }
.card h3 { font-size: 18px; margin-bottom: 8px; }
.card .meta { color: #b45309; font-size: 14px; margin-bottom: 8px; }
.card .desc { color: #666; font-size: 13px; line-height: 1.6; height: 62px; overflow: hidden; }
.card .actions { margin-top: 10px; display: flex; gap: 8px; }
button { cursor: pointer; border: none; border-radius: 4px; padding: 8px 14px; font-size: 14px; }
.btn { background: #b45309; color: #fff; }
.btn.faved { background: #e2e8f0; color: #666; }
.btn-gray { background: #e2e8f0; color: #333; }
.searchbar { margin-bottom: 20px; display: flex; gap: 8px; }
.searchbar input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.pager { margin-top: 20px; display: flex; gap: 8px; align-items: center; justify-content: center; }
.detail { background: #fff; border-radius: 8px; padding: 24px; }
.detail h2 { margin-bottom: 12px; }
.detail .meta { color: #b45309; margin-bottom: 12px; }
.detail p { line-height: 1.8; color: #555; }
.detail img { max-width: 100%; border-radius: 8px; margin: 12px 0; }
.chat-box { background: #fff; border-radius: 8px; padding: 20px; }
.chat-box textarea { width: 100%; height: 90px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; resize: vertical; }
.chat-answer { margin-top: 16px; background: #f6f7f9; border-radius: 6px; padding: 14px; line-height: 1.8; white-space: pre-wrap; }
.empty { text-align: center; color: #999; padding: 60px 0; }
.loading { text-align: center; color: #999; padding: 30px 0; }
.stores { margin-top: 12px; }
.stores li { margin: 6px 0; color: #555; }
```

- [ ] **Step 3: 写 utils.js 与 api.js**

`frontend/js/utils.js`：
```javascript
function getDeviceId() {
  let id = localStorage.getItem("device_id");
  if (!id) {
    id = (crypto.randomUUID && crypto.randomUUID())
      || ("dev-" + Date.now() + "-" + Math.random().toString(16).slice(2));
    localStorage.setItem("device_id", id);
  }
  return id;
}

function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}
```

`frontend/js/api.js`：
```javascript
const API_BASE = "http://localhost:8000/api";

async function request(method, path, body) {
  const headers = { "X-Device-Id": getDeviceId() };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const resp = await fetch(API_BASE + path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (resp.status === 204) return null;
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.detail || "请求失败");
  return data;
}

const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  del: (path) => request("DELETE", path),
};
```

- [ ] **Step 4: 写 app.js（路由 + 导航）**

`frontend/js/app.js`：
```javascript
const routes = {
  foods: () => FoodView.list(),
  attractions: () => AttractionView.list(),
  ai: () => AIView.render(),
  favorites: () => FavoriteView.list(),
};

function renderHome() {
  const view = document.getElementById("view");
  view.innerHTML = `
    <div class="detail">
      <h2>欢迎来到南昌</h2>
      <p>探索南昌特色美食与旅游景点，还能用 AI 帮你规划游玩攻略。</p>
      <div class="card-grid" style="margin-top:16px">
        <div class="card"><div class="card-body"><h3>🍜 美食</h3><p class="desc">南昌拌粉、瓦罐汤、藜蒿炒腊肉……</p></div></div>
        <div class="card"><div class="card-body"><h3>🏞️ 景点</h3><p class="desc">滕王阁、八一广场、绳金塔……</p></div></div>
        <div class="card"><div class="card-body"><h3>🤖 AI 攻略</h3><p class="desc">输入问题，一键生成南昌游玩攻略。</p></div></div>
      </div>
    </div>`;
}

function setActiveNav(view) {
  document.querySelectorAll(".nav a").forEach((a) => {
    a.classList.toggle("active", a.dataset.view === view);
  });
}

function router() {
  const hash = location.hash || "#/";
  const view = document.getElementById("view");
  setActiveNav("");
  if (hash === "#/" || hash === "#/home") return renderHome();
  const [name, id] = hash.slice(2).split("/");
  if (name === "foods" && id) return FoodView.detail(id);
  if (name === "attractions" && id) return AttractionView.detail(id);
  const handler = routes[name];
  if (handler) {
    setActiveNav(name);
    handler();
  } else {
    view.innerHTML = `<div class="empty">页面不存在</div>`;
  }
}

window.addEventListener("hashchange", router);
router();
```

- [ ] **Step 5: 人工验证**

```bash
cd /d/yammy/frontend && python -m http.server 5500
```
浏览器打开 `http://localhost:5500`，确认导航栏与首页渲染正常（列表尚未实现，属下一任务）。

- [ ] **Step 6: 提交**

```bash
cd /d/yammy && git add frontend && git commit -m "feat: 前端骨架（布局/路由/api 封装）"
```

---

## Task 8: 前端页面（美食 / 景点 / AI / 收藏）

**Files:**
- Create: `frontend/js/food.js`, `frontend/js/attraction.js`, `frontend/js/ai.js`, `frontend/js/favorite.js`
- Test: 无自动化测试（人工浏览器验证）

**Interfaces:**
- Consumes: 全局 `api`、`el`；`FoodView` / `AttractionView` / `AIView` / `FavoriteView` 四个全局对象被 `app.js` 调用。

- [ ] **Step 1: 写 food.js**

`frontend/js/food.js`：
```javascript
const FoodView = {
  async list() {
    const view = document.getElementById("view");
    view.innerHTML = `
      <div class="searchbar">
        <input id="food-kw" placeholder="搜索美食（名称/简介）">
        <button class="btn" id="food-search">搜索</button>
      </div>
      <div id="food-grid" class="card-grid"><div class="loading">加载中…</div></div>
      <div id="food-pager" class="pager"></div>`;
    await this._load(1);
    document.getElementById("food-search").onclick = () => this._load(1, document.getElementById("food-kw").value);
  },

  async _load(page, keyword = "") {
    const grid = document.getElementById("food-grid");
    const pager = document.getElementById("food-pager");
    const q = `page=${page}&page_size=9&keyword=${encodeURIComponent(keyword)}`;
    const data = await api.get(`/foods?${q}`);
    if (data.items.length === 0) {
      grid.innerHTML = `<div class="empty">暂无美食数据</div>`;
      pager.innerHTML = "";
      return;
    }
    grid.innerHTML = data.items.map((f) => `
      <div class="card">
        <img src="${f.image_url || ""}" onerror="this.style.display='none'" alt="${f.name}">
        <div class="card-body">
          <h3>${f.name}</h3>
          <div class="meta">人均 ¥${f.avg_price}</div>
          <p class="desc">${f.description}</p>
          <div class="actions">
            <button class="btn" onclick="location.hash='#/foods/${f.id}'">查看详情</button>
            <button class="btn ${FavoriteView.isFaved("food", f.id) ? "faved" : ""}" onclick="FavoriteView.toggle('food', ${f.id}, this)">${FavoriteView.isFaved("food", f.id) ? "已收藏" : "收藏"}</button>
          </div>
        </div>
      </div>`).join("");
    pager.innerHTML = `第 ${data.page} / ${Math.ceil(data.total / data.page_size) || 1} 页`;
  },

  async detail(id) {
    const view = document.getElementById("view");
    const f = await api.get(`/foods/${id}`);
    view.innerHTML = `
      <div class="detail">
        <h2>${f.name}</h2>
        <div class="meta">人均 ¥${f.avg_price}</div>
        <img src="${f.image_url || ""}" onerror="this.style.display='none'" alt="${f.name}">
        <p>${f.description}</p>
        <div class="stores"><strong>推荐门店：</strong><ul>${f.stores.map((s) => `<li>${s.name}${s.address ? "（" + s.address + "）" : ""}</li>`).join("") || "<li>暂无</li>"}</ul></div>
      </div>`;
  },
};
```

> 说明：收藏按钮用本地 `favedFoods` 集合渲染状态（见 Task 8 Step 4），为免重复请求。

- [ ] **Step 2: 写 attraction.js**

`frontend/js/attraction.js`：
```javascript
const AttractionView = {
  async list() {
    const view = document.getElementById("view");
    view.innerHTML = `
      <div class="searchbar">
        <input id="att-kw" placeholder="搜索景点（名称/简介）">
        <button class="btn" id="att-search">搜索</button>
      </div>
      <div id="att-grid" class="card-grid"><div class="loading">加载中…</div></div>
      <div id="att-pager" class="pager"></div>`;
    await this._load(1);
    document.getElementById("att-search").onclick = () => this._load(1, document.getElementById("att-kw").value);
  },

  async _load(page, keyword = "") {
    const grid = document.getElementById("att-grid");
    const pager = document.getElementById("att-pager");
    const q = `page=${page}&page_size=9&keyword=${encodeURIComponent(keyword)}`;
    const data = await api.get(`/attractions?${q}`);
    if (data.items.length === 0) {
      grid.innerHTML = `<div class="empty">暂无景点数据</div>`;
      pager.innerHTML = "";
      return;
    }
    grid.innerHTML = data.items.map((a) => `
      <div class="card">
        <img src="${a.image_url || ""}" onerror="this.style.display='none'" alt="${a.name}">
        <div class="card-body">
          <h3>${a.name}</h3>
          <div class="meta">${a.ticket_price} · ${a.open_time}</div>
          <p class="desc">${a.description}</p>
          <div class="actions">
            <button class="btn" onclick="location.hash='#/attractions/${a.id}'">查看详情</button>
            <button class="btn ${FavoriteView.isFaved("attraction", a.id) ? "faved" : ""}" onclick="FavoriteView.toggle('attraction', ${a.id}, this)">${FavoriteView.isFaved("attraction", a.id) ? "已收藏" : "收藏"}</button>
          </div>
        </div>
      </div>`).join("");
    pager.innerHTML = `第 ${data.page} / ${Math.ceil(data.total / data.page_size) || 1} 页`;
  },

  async detail(id) {
    const view = document.getElementById("view");
    const a = await api.get(`/attractions/${id}`);
    view.innerHTML = `
      <div class="detail">
        <h2>${a.name}</h2>
        <div class="meta">开放时间 ${a.open_time} · 门票 ${a.ticket_price}</div>
        <img src="${a.image_url || ""}" onerror="this.style.display='none'" alt="${a.name}">
        <p>${a.description}</p>
      </div>`;
  },
};
```

- [ ] **Step 3: 写 ai.js**

`frontend/js/ai.js`：
```javascript
const AIView = {
  render() {
    const view = document.getElementById("view");
    view.innerHTML = `
      <div class="chat-box">
        <h2 style="margin-bottom:12px">AI 游玩咨询</h2>
        <textarea id="ai-question" placeholder="例如：帮我规划一天南昌美食行程"></textarea>
        <div style="margin-top:10px"><button class="btn" id="ai-ask">提问</button></div>
        <div id="ai-answer"></div>
      </div>`;
    document.getElementById("ai-ask").onclick = () => this.ask();
  },

  async ask() {
    const q = document.getElementById("ai-question").value.trim();
    const box = document.getElementById("ai-answer");
    if (!q) { box.innerHTML = `<div class="empty">请输入问题</div>`; return; }
    box.innerHTML = `<div class="loading">正在思考…</div>`;
    try {
      const data = await api.post("/ai/consult", { question: q });
      const refs = [
        ...data.references.foods.map((f) => `<button class="btn-gray" onclick="location.hash='#/foods/${f.id}'">🍜 ${f.name}</button>`),
        ...data.references.attractions.map((a) => `<button class="btn-gray" onclick="location.hash='#/attractions/${a.id}'">🏞️ ${a.name}</button>`),
      ].join(" ");
      box.innerHTML = `<div class="chat-answer">${data.answer}</div>${refs ? `<div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">相关推荐：${refs}</div>` : ""}`;
    } catch (e) {
      box.innerHTML = `<div class="empty">${e.message}</div>`;
    }
  },
};
```

- [ ] **Step 4: 写 favorite.js**

`frontend/js/favorite.js`：
```javascript
const FavoriteView = {
  _cache: { food: new Set(), attraction: new Set() },

  isFaved(type, id) {
    return this._cache[type] && this._cache[type].has(String(id));
  },

  async toggle(type, id, btn) {
    const key = type === "food" ? "food" : "attraction";
    try {
      if (this.isFaved(key, id)) {
        await api.del(`/favorites/${type}/${id}`);
        this._cache[key].delete(String(id));
        if (btn) { btn.textContent = "收藏"; btn.classList.remove("faved"); }
      } else {
        await api.post("/favorites", { target_type: type, target_id: id });
        this._cache[key].add(String(id));
        if (btn) { btn.textContent = "已收藏"; btn.classList.add("faved"); }
      }
    } catch (e) {
      alert(e.message);
    }
  },

  async list() {
    const view = document.getElementById("view");
    view.innerHTML = `<div class="card-grid" id="fav-grid"><div class="loading">加载中…</div></div>`;
    const data = await api.get("/favorites?page=1&page_size=100");
    const grid = document.getElementById("fav-grid");
    if (data.items.length === 0) {
      grid.innerHTML = `<div class="empty">暂无收藏</div>`;
      return;
    }
    grid.innerHTML = data.items.map((it) => {
      const obj = it.food || it.attraction;
      const isFood = !!it.food;
      return `
        <div class="card">
          <div class="card-body">
            <h3>${obj.name}</h3>
            <div class="meta">${isFood ? "人均 ¥" + obj.avg_price : obj.ticket_price}</div>
            <div class="actions">
              <button class="btn" onclick="location.hash='#/${isFood ? "foods" : "attractions"}/${obj.id}'">查看</button>
              <button class="btn faved" onclick="FavoriteView.toggle('${isFood ? "food" : "attraction"}', ${obj.id}, this)">取消收藏</button>
            </div>
          </div>
        </div>`;
    }).join("");
  },
};
```

- [ ] **Step 5: 人工联调验证**

```bash
# 终端 A：后端（先完成 Task 6 种子）
cd /d/yammy/backend && source .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000
# 终端 B：前端
cd /d/yammy/frontend && python -m http.server 5500
```
验证：美食/景点列表与详情、搜索、AI 问答（需真实 `DEEPSEEK_API_KEY`）、收藏增删与「我的收藏」均正常。

- [ ] **Step 6: 提交**

```bash
cd /d/yammy && git add frontend && git commit -m "feat: 前端页面（美食/景点/AI/收藏）"
```

---

## Task 9: 模块实现报告 + README

**Files:**
- Create: `docs/implements/food.md`, `docs/implements/attraction.md`, `docs/implements/ai.md`, `docs/implements/favorite.md`
- Create: `backend/README.md`
- Test: `cd /d/yammy/backend && python -m pytest -v`（全量回归，预期 21 passed）

**Interfaces:** 无（文档任务）

- [ ] **Step 1: 写四份模块实现报告**

`docs/implements/food.md`：
```markdown
# 美食模块实现报告

- 职责：美食列表/详情/搜索，含推荐门店。
- 分层：`model.py`（Food/Store）、`schema.py`（StoreOut/FoodOut/FoodListOut/FoodBrief）、`repository.py`（list/get_by_id/list_all/search）、`service.py`（list_foods/get_food）、`router.py`。
- 接口：`GET /api/foods`、`GET /api/foods/{id}`。
- 测试：`tests/test_food.py`（4 用例，覆盖列表/搜索/详情含门店/404）。
```

`docs/implements/attraction.md`：
```markdown
# 景点模块实现报告

- 职责：景点列表/详情/搜索。
- 分层：`model.py`（Attraction）、`schema.py`（AttractionOut/AttractionListOut/AttractionBrief）、`repository.py`（list/get_by_id/list_all/search）、`service.py`、`router.py`。
- 接口：`GET /api/attractions`、`GET /api/attractions/{id}`。
- 测试：`tests/test_attraction.py`（4 用例）。
```

`docs/implements/ai.md`：
```markdown
# AI 咨询模块实现报告

- 职责：DeepSeek 游玩咨询，注入本地美食/景点数据，一次性返回。
- 分层：`schema.py`（ConsultRequest/ConsultResponse）、`deepseek_client.py`（懒初始化 OpenAI 客户端）、`context_builder.py`（实体名反向匹配 + LIKE 兜底，构建 prompt）、`service.py`（consult）、`router.py`。
- 接口：`POST /api/ai/consult`。
- 测试：`tests/test_ai.py`（4 用例，mock DeepSeek，校验答案/上下文注入/422/502）。
```

`docs/implements/favorite.md`：
```markdown
# 收藏模块实现报告

- 职责：收藏增删查与状态查询，按匿名设备标识 `X-Device-Id` 持久化。
- 分层：`model.py`（Favorite，唯一约束）、`schema.py`、`repository.py`（get/add/delete/list）、`service.py`（幂等/目标校验/列表聚合）、`router.py`。
- 接口：`GET /api/favorites`、`POST /api/favorites`、`DELETE /api/favorites/{target_type}/{target_id}`、`GET /api/favorites/status`。
- 测试：`tests/test_favorite.py`（8 用例）。
```

- [ ] **Step 2: 写 backend/README.md**

`backend/README.md`：
```markdown
# 南昌旅游美食推荐平台 · 后端

## 环境
Python 3.11+、MySQL 8.0+。

## 安装
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash；PowerShell 用 .venv\Scripts\Activate.ps1
pip install -r requirements.txt

## 配置
复制 .env.example 为 .env，填写 DATABASE_URL 与 DEEPSEEK_API_KEY。

## 数据库与种子
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS nanchang_travel CHARACTER SET utf8mb4;"
python -m seed.seed

## 运行
uvicorn app.main:app --reload --port 8000

## 测试
python -m pytest -v
```

- [ ] **Step 3: 全量回归测试**

Run: `cd /d/yammy/backend && python -m pytest -v`
Expected: 21 passed（health 1 + food 4 + attraction 4 + favorite 8 + ai 4）

- [ ] **Step 4: 提交**

```bash
cd /d/yammy && git add docs backend/README.md && git commit -m "docs: 模块实现报告 + README"
```

---

## 自审记录（Self-Review）

- **Spec 覆盖**：PRD 核心功能逐一对应——美食(§3.1→Task2)、景点(§3.2→Task3)、AI(§3.3→Task5)、收藏(§3.4→Task4)、数据模型(§4→各 model)、图片(§4.3→Task6)、API(§6→各 router)、AI 检索(§7→context_builder)、测试(§9→各 test)、文档(§10→Task9)。无遗漏。
- **占位符扫描**：无 TBD/TODO；所有代码步骤均给出完整代码。
- **类型一致性**：`FoodOut/FoodBrief/StoreOut` 等 schema 名在 service、ai、favorite、测试间一致；`get_device_id` 统一取自 `app.core.deps`；`DeepSeekClient.chat` 签名一致。
- **已知取舍**：Pydantic 请求体校验错误返回 422（FastAPI 默认），PRD 的「400 参数非法」指业务校验（如 target_type 非法），二者并存，已在测试中分别断言 422 与 400。
