from datetime import datetime

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship

from src.schemas.base import BaseSQLModel


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


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

    categories: list["Category"] = Relationship(back_populates="user")  # noqa: F821
    tags: list["Tag"] = Relationship(back_populates="user")  # noqa: F821
    transactions: list["Transaction"] = Relationship(back_populates="user")  # noqa: F821
    goals: list["Goal"] = Relationship(back_populates="user")  # noqa: F821
    budgets: list["Budget"] = Relationship(back_populates="user")  # noqa: F821


class UserUpdate(BaseSQLModel):
    username: str | None = None
    birth_date: datetime | None = None

    @classmethod
    def custom_validate(cls, birth_date: datetime) -> None:
        cls.validate_past_data(date=birth_date, field_name="birth_date")
