from pydantic import BaseModel, ConfigDict


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str | None = None


class FoodBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    avg_price: float
    image_url: str | None = None


class FoodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    avg_price: float
    image_url: str | None = None
    stores: list[StoreOut] = []


class FoodListOut(BaseModel):
    items: list[FoodOut]
    total: int
    page: int
    page_size: int
