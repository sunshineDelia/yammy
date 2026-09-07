from pydantic import BaseModel, Field

from app.modules.attraction.schema import AttractionBrief
from app.modules.food.schema import FoodBrief


class ConsultRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class ConsultReferences(BaseModel):
    foods: list[FoodBrief]
    attractions: list[AttractionBrief]


class ConsultResponse(BaseModel):
    answer: str
    references: ConsultReferences
