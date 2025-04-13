from pydantic import BaseModel, PastDate
from decimal import Decimal
from datetime import date


class TransactionCreateRequest(BaseModel):
    user_id: int
    category_id: int
    amount: Decimal
    date: PastDate
    description: str


class TransactionUpdateRequest(BaseModel):
    amount: Decimal | None
    date: PastDate | None
    description: str | None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    date: PastDate
    description: str

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: str


class TransactionWithCategoryResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: float
    date: date
    description: str
    category: CategoryResponse


