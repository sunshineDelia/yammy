from pydantic import BaseModel, ConfigDict


class AttractionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ticket_price: str
    image_url: str | None = None


class AttractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    open_time: str
    ticket_price: str
    image_url: str | None = None


class AttractionListOut(BaseModel):
    items: list[AttractionOut]
    total: int
    page: int
    page_size: int
