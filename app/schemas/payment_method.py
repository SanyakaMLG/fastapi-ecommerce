from pydantic import BaseModel, Field


class PaymentMethodBase(BaseModel):
    card_number: str = Field(max_length=255)

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodUpdate(PaymentMethodBase):
    pass
