from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    parent_id: int = Field(default=None)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int