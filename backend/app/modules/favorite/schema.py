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
