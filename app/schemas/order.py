from typing import Optional

from pydantic import BaseModel, Field

from app.models import OrderStatus, DeliveryType


class OrderCreate(BaseModel):
    delivery_type: DeliveryType
    delivery_address: Optional[int] = Field(ge=0, default=None)
    payment_method_id: int = Field(ge=0)


class OrderBase(OrderCreate):
    status: OrderStatus = Field(default=OrderStatus.new)
    cart_id: int = Field(ge=0)


class OrderRead(OrderBase):
    cart_cost: float
    delivery_cost: float
    id: int
