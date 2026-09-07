from typing import Literal

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
    sort: Literal["id", "rating"] = "id",
    db: Session = Depends(get_db),
):
    return FoodService(FoodRepository(db)).list_foods(page, page_size, keyword, sort)


@router.get("/{food_id}", response_model=FoodOut)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = FoodService(FoodRepository(db)).get_food(food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="美食不存在")
    return food
