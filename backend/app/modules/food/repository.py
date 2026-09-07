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
