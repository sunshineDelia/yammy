from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import BigIntType


class Food(Base):
    __tablename__ = "food"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    avg_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    stores: Mapped[list["Store"]] = relationship(
        back_populates="food", cascade="all, delete-orphan"
    )


class Store(Base):
    __tablename__ = "store"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)
    food_id: Mapped[int] = mapped_column(BigIntType, ForeignKey("food.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    food: Mapped["Food"] = relationship(back_populates="stores")
