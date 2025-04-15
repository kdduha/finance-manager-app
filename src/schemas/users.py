from pydantic import EmailStr
from sqlmodel import Field, Relationship
from datetime import datetime

from src.schemas.base import BaseSQLModel


class UserDefault(BaseSQLModel):
    username: str
    email: EmailStr
    password: str
    birth_date: datetime

    @classmethod
    def custom_validate(cls, birth_date: datetime) -> None:
        cls.validate_past_data(date=birth_date, field_name="birth_date")


class User(UserDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime

    categories: list["Category"] = Relationship(back_populates="user")
    tags: list["Tag"] = Relationship(back_populates="user")
    transactions: list["Transaction"] = Relationship(back_populates="user")
    goals: list["Goal"] = Relationship(back_populates="user")
    budgets: list["Budget"] = Relationship(back_populates="user")


class UserUpdate(BaseSQLModel):
    username: str | None = None
    email: EmailStr | None = None
    birth_date: datetime | None = None

    @classmethod
    def custom_validate(cls, birth_date: datetime) -> None:
        cls.validate_past_data(date=birth_date, field_name="birth_date")

