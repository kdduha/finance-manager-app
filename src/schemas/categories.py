from pydantic import BaseModel
from enum import Enum


class CategoryType(Enum):
    income = "income"
    expense = "expense"


class CategoryCreateRequest(BaseModel):
    name: str
    type: CategoryType
    user_id: int


class CategoryUpdateRequest(BaseModel):
    name: str | None
    type: CategoryType | str


class CategoryResponse(BaseModel):
    id: str
    name: str
    type: CategoryType
    user_id: int

    class Config:
        from_attributes = True
