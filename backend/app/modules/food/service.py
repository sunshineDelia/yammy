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
