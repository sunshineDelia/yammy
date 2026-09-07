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
