from enum import Enum
from sqlmodel import Field, Relationship
from datetime import datetime
from decimal import Decimal

from src.schemas.base import BaseSQLModel


class CategoryType(Enum):
    income = "income"
    expense = "expense"


class CategoryDefault(BaseSQLModel):
    name: str
    type: CategoryType
    user_id: int = Field(foreign_key="user.id")


class Category(CategoryDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="categories")
    transactions: list["Transaction"] = Relationship(back_populates="category")
    budgets: list["Budget"] = Relationship(back_populates="category")


class CategoryUpdate(BaseSQLModel):
    name: str | None


class TransactionWithCategory(BaseSQLModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    date: datetime
    description: str | None = None
    category: Category
