from pydantic import BaseModel, FutureDate, PastDate
from decimal import Decimal


class BudgetCreateRequest(BaseModel):
    user_id: int
    category_id: int
    limit_amount: Decimal
    end_date: FutureDate


class BudgetUpdateRequest(BaseModel):
    limit_amount: Decimal
    end_date: FutureDate


class BudgetResponse(BaseModel):
    id: str
    user_id: int
    category_id: int
    limit_amount: Decimal
    start_date: PastDate
    end_date: FutureDate

    class Config:
        from_attributes = True
