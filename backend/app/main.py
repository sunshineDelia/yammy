from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.modules.attraction.router import router as attraction_router
from app.modules.favorite.router import router as favorite_router
from app.modules.food.router import router as food_router

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

app.include_router(food_router, prefix="/api")
app.include_router(attraction_router, prefix="/api")
app.include_router(favorite_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
