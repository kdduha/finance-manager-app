from sqlmodel import Field, Relationship
from datetime import datetime
from decimal import Decimal

from src.schemas.base import BaseSQLModel


class GoalDefault(BaseSQLModel):
    name: str
    deadline: datetime
    target_amount: Decimal
    current_amount: Decimal
    user_id: int = Field(foreign_key="user.id")

    @classmethod
    def custom_validate(cls, deadline: datetime) -> None:
        cls.validate_future_date(date=deadline, field_name="deadline")


class Goal(GoalDefault, table=True):
    id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime

    user: "User" = Relationship(back_populates="goals")


class GoalUpdate(BaseSQLModel):
    name: str | None = None
    deadline: datetime | None = None
    target_amount: Decimal | None = None
    current_amount: Decimal | None = None

    @classmethod
    def custom_validate(cls, deadline: datetime) -> None:
        cls.validate_future_date(date=deadline, field_name="deadline")
