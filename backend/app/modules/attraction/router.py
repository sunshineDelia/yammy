from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.modules.attraction.repository import AttractionRepository
from app.modules.attraction.schema import AttractionListOut, AttractionOut
from app.modules.attraction.service import AttractionService

router = APIRouter(prefix="/attractions", tags=["attractions"])


@router.get("", response_model=AttractionListOut)
def list_attractions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = None,
    sort: Literal["id", "rating"] = "id",
    db: Session = Depends(get_db),
):
    return AttractionService(AttractionRepository(db)).list_attractions(page, page_size, keyword, sort)


@router.get("/{attraction_id}", response_model=AttractionOut)
def get_attraction(attraction_id: int, db: Session = Depends(get_db)):
    attraction = AttractionService(AttractionRepository(db)).get_attraction(attraction_id)
    if attraction is None:
        raise HTTPException(status_code=404, detail="景点不存在")
    return attraction
