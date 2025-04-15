from sqlmodel import Field, Relationship
from datetime import datetime
from decimal import Decimal

from src.schemas.base import BaseSQLModel


class BudgetDefault(BaseSQLModel):
    limit_amount: Decimal
    start_date: datetime
    end_date: datetime

    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    @classmethod
    def custom_validate(cls, start_date: datetime, end_date: datetime) -> None:
        cls.validate_past_data(date=start_date, field_name="start_date")
        cls.validate_future_date(date=end_date, field_name="end_date")


class Budget(BudgetDefault, table=True):
    id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime

    user: "User" = Relationship(back_populates="budgets")
    category: "Category" = Relationship(back_populates="budgets")


class BudgetUpdate(BaseSQLModel):
    limit_amount: Decimal | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None

    @classmethod
    def custom_validate(cls, start_date: datetime, end_date: datetime) -> None:
        cls.validate_past_data(date=start_date, field_name="start_date")
        cls.validate_future_date(date=end_date, field_name="end_date")

