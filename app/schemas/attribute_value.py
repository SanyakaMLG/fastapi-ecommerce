from pydantic import BaseModel, Field, model_validator


class AttributeValueBase(BaseModel):
    attribute_id: int
    value: str = Field(max_length=255)

class AttributeValueCreate(AttributeValueBase):
    pass

class AttributeValueUpdate(AttributeValueBase):
    pass

