from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_device_id
from app.modules.attraction.repository import AttractionRepository
from app.modules.favorite.repository import FavoriteRepository
from app.modules.favorite.schema import FavoriteCreate, FavoriteListOut, FavoriteStatus
from app.modules.favorite.service import FavoriteService
from app.modules.food.repository import FoodRepository

router = APIRouter(prefix="/favorites", tags=["favorites"])


def _service(db: Session) -> FavoriteService:
    return FavoriteService(FavoriteRepository(db), FoodRepository(db), AttractionRepository(db))


@router.get("", response_model=FavoriteListOut)
def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    return _service(db).list_favorites(device_id, page, page_size)


@router.post("")
def add_favorite(
    payload: FavoriteCreate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    fav, created = _service(db).add(device_id, payload.target_type, payload.target_id)
    return JSONResponse(
        status_code=201 if created else 200,
        content={"target_type": fav.target_type, "target_id": fav.target_id},
    )


@router.delete("/{target_type}/{target_id}", status_code=204)
def remove_favorite(
    target_type: str,
    target_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    if not _service(db).remove(device_id, target_type, target_id):
        raise HTTPException(status_code=404, detail="收藏不存在")
    return Response(status_code=204)


@router.get("/status", response_model=FavoriteStatus)
def favorite_status(
    target_type: str,
    target_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    return _service(db).status(device_id, target_type, target_id)
