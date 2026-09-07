from pydantic import BaseModel, ConfigDict, Field


class AttractionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ticket_price: str
    rating: float
    level: str
    image_url: str | None = None


class AttractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    open_time: str
    ticket_price: str
    rating: float
    rating_count: int
    level: str
    duration: str
    address: str | None = None
    tags: list[str] = Field(default_factory=list)
    image_url: str | None = None


class AttractionListOut(BaseModel):
    items: list[AttractionOut]
    total: int
    page: int
    page_size: int
