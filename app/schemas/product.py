from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = Field(max_length=255)
    price: float = Field(ge=0)
    discount: float | None = Field(ge=0, le=100)
    quantity: int = Field(ge=0)
    category_id: int
    attribute_values: list[int] | None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int