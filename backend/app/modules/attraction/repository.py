from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.attraction.model import Attraction


class AttractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, page: int, page_size: int, keyword: str | None = None) -> tuple[list[Attraction], int]:
        stmt = select(Attraction)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Attraction.name.like(like), Attraction.description.like(like)))
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Attraction.id).offset((page - 1) * page_size).limit(page_size)
            )
        )
        return items, total

    def get_by_id(self, attraction_id: int) -> Attraction | None:
        return self.db.scalar(select(Attraction).where(Attraction.id == attraction_id))

    def list_all(self) -> list[Attraction]:
        return list(self.db.scalars(select(Attraction)))

    def search(self, keyword: str, limit: int = 5) -> list[Attraction]:
        like = f"%{keyword}%"
        stmt = (
            select(Attraction)
            .where(or_(Attraction.name.like(like), Attraction.description.like(like)))
            .limit(limit)
        )
        return list(self.db.scalars(stmt))
