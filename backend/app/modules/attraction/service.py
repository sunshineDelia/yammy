from app.modules.attraction.repository import AttractionRepository
from app.modules.attraction.schema import AttractionListOut, AttractionOut


class AttractionService:
    def __init__(self, repo: AttractionRepository):
        self.repo = repo

    def list_attractions(self, page: int, page_size: int, keyword: str | None = None) -> AttractionListOut:
        items, total = self.repo.list(page, page_size, keyword)
        return AttractionListOut(
            items=[AttractionOut.model_validate(a) for a in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_attraction(self, attraction_id: int) -> AttractionOut | None:
        attraction = self.repo.get_by_id(attraction_id)
        return AttractionOut.model_validate(attraction) if attraction else None
