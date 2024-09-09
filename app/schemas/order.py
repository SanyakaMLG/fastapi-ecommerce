from pydantic import BaseModel, Field

from app.models import OrderStatus, DeliveryType


class OrderBase(BaseModel):
    cart_id: int = Field(ge=0)
    status: OrderStatus = Field(default=OrderStatus.new)
    delivery_type: DeliveryType
    delivery_address: int | None = Field(ge=0)
    payment_method_id: int = Field(ge=0)

class OrderCreate(OrderBase):
    pass

class OrderRead(OrderBase):
    cart_cost: float
    delivery_cost: float
    id: int
