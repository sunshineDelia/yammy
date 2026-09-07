# 南昌旅游美食推荐平台 · 后端

## 环境
Python 3.11+、MySQL 8.0+。

## 安装
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash；PowerShell 用 .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 配置
复制 `.env.example` 为 `.env`，填写 `DATABASE_URL` 与 `DEEPSEEK_API_KEY`。

## 数据库与种子
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS nanchang_travel CHARACTER SET utf8mb4;"
python -m seed.seed
```

## 运行
```bash
uvicorn app.main:app --reload --port 8000
```

## 前端
另开终端：`cd frontend && python -m http.server 5500`，浏览器打开 http://localhost:5500。

## 测试
```bash
python -m pytest -v
```
