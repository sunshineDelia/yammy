from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.food.model import Food


def _keyword_filter(stmt, keyword: str):
    like = f"%{keyword}%"
    return stmt.where(or_(Food.name.like(like), Food.description.like(like)))


class FoodRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, page: int, page_size: int, keyword: str | None = None) -> tuple[list[Food], int]:
        stmt = select(Food)
        if keyword:
            stmt = _keyword_filter(stmt, keyword)
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
        return list(self.db.scalars(select(Food).options(selectinload(Food.stores)).order_by(Food.id)))

    def search(self, keyword: str, limit: int = 5) -> list[Food]:
        stmt = (
            _keyword_filter(select(Food).options(selectinload(Food.stores)), keyword)
            .order_by(Food.id)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def get_by_ids(self, ids: list[int]) -> list[Food]:
        if not ids:
            return []
        return list(self.db.scalars(select(Food).where(Food.id.in_(ids))))
