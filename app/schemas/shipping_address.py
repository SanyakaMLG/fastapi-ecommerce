from pydantic import BaseModel, Field


class ShippingAddressBase(BaseModel):
    address: str = Field(max_length=255)
    city: str = Field(max_length=255)
    state: str = Field(max_length=255)
    country: str = Field(max_length=255)
    postal_code: str = Field(max_length=255)


class ShippingAddressCreate(ShippingAddressBase):
    pass


class ShippingAddressUpdate(ShippingAddressBase):
    pass
