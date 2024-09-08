from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(max_length=255)


class ReviewCreate(ReviewBase):
    product_id: int


class ReviewUpdate(ReviewBase):
    pass
