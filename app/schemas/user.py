from fastapi_users import schemas
from pydantic import ConfigDict, Field


class UserRead(schemas.BaseUser[int]):
    phone: str
    first_name: str
    last_name: str
    middle_name: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    phone: str = Field(pattern=r"[0-9]+", min_length=8, max_length=20)
    first_name: str
    last_name: str
    middle_name: str


class UserUpdate(schemas.BaseUserUpdate):
    phone: str
    first_name: str
    last_name: str
    middle_name: str