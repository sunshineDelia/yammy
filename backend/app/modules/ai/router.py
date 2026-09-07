from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.modules.ai.context_builder import ContextBuilder
from app.modules.ai.deepseek_client import DeepSeekClient, DeepSeekError
from app.modules.ai.schema import ConsultRequest, ConsultResponse
from app.modules.ai.service import AIService
from app.modules.attraction.repository import AttractionRepository
from app.modules.food.repository import FoodRepository

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/consult", response_model=ConsultResponse)
def consult(payload: ConsultRequest, db: Session = Depends(get_db)):
    service = AIService(
        ContextBuilder(FoodRepository(db), AttractionRepository(db)),
        DeepSeekClient(),
    )
    try:
        return service.consult(payload.question)
    except DeepSeekError:
        raise HTTPException(status_code=502, detail="AI 服务调用失败")
