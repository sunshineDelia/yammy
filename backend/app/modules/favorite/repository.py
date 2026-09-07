from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.favorite.model import Favorite


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, device_id: str, target_type: str, target_id: int) -> Favorite | None:
        return self.db.scalar(
            select(Favorite).where(
                Favorite.device_id == device_id,
                Favorite.target_type == target_type,
                Favorite.target_id == target_id,
            )
        )

    def add(self, device_id: str, target_type: str, target_id: int) -> Favorite:
        fav = Favorite(device_id=device_id, target_type=target_type, target_id=target_id)
        self.db.add(fav)
        self.db.commit()
        self.db.refresh(fav)
        return fav

    def delete(self, device_id: str, target_type: str, target_id: int) -> bool:
        fav = self.get(device_id, target_type, target_id)
        if fav is None:
            return False
        self.db.delete(fav)
        self.db.commit()
        return True

    def list(self, device_id: str, page: int, page_size: int) -> tuple[list[Favorite], int]:
        stmt = select(Favorite).where(Favorite.device_id == device_id)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Favorite.id.desc()).offset((page - 1) * page_size).limit(page_size)
            )
        )
        return items, total
