# 南昌旅游美食推荐平台 · 后端

> 面向游客的 PC 端网站后端，提供南昌美食/景点展示、AI 游玩咨询、收藏功能。

## 技术栈
Python 3.11+ · FastAPI · SQLAlchemy 2.0 · MySQL 8.0 · DeepSeek 大模型

## 目录结构
```
backend/
├─ app/
│  ├─ main.py                 # FastAPI 入口：注册全部路由 + 静态资源 + 前端托管
│  ├─ core/                   # config / database / deps / types
│  └─ modules/                # 一个业务模块一个包
│     ├─ food/                #   美食（model/schema/repository/service/router）
│     ├─ attraction/          #   景点
│     ├─ ai/                  #   AI 咨询（DeepSeek + 本地数据注入）
│     └─ favorite/            #   收藏
├─ docs/implements/           # 各模块技术实现文档
├─ tests/                     # 单元测试（42 个，SQLite 隔离 + mock DeepSeek）
├─ seed/seed.py               # 预置种子数据（60 美食 + 60 景点）
├─ static/images/             # 图片（真实图 + 通用图池）
├─ script.sql                 # MySQL 建库建表脚本
├─ requirements.txt
└─ .env.example
```

## 快速开始

```bash
cd backend

# 1. 安装依赖
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash；PowerShell 用 .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. 配置
cp .env.example .env               # 填 DATABASE_URL 与 DEEPSEEK_API_KEY

# 3. 建库 + 种子数据
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS nanchang_travel CHARACTER SET utf8mb4;"
python -m seed.seed

# 4. 运行（一个服务同时托管前端页面 + API）
uvicorn app.main:app --reload --port 8000
```

浏览器打开 **http://localhost:8000** 即可使用完整网站（前端已由后端托管，无需另起前端服务）。

## 测试
```bash
python -m pytest -v
```

## 说明
- 前端为原生 HTML/CSS/JS，位于仓库根目录 `frontend/`，由 FastAPI 在 `/` 挂载托管；API 统一走 `/api` 同源调用。
- 收藏按匿名设备标识 `X-Device-Id` 持久化，无需登录。
- 图片来自 Wikimedia Commons（免费许可），来源与许可详见 `static/images/README.md`。
