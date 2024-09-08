from pydantic import BaseModel, Field


class AttributeBase(BaseModel):
    title: str = Field(max_length=255)
    in_filter: bool

class AttributeCreate(AttributeBase):
    pass

class AttributeUpdate(AttributeBase):
    pass
