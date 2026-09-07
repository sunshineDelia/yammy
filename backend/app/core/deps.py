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
