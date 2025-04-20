from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel

from src.schemas.base import BaseSQLModel


class TransactionTagLink(SQLModel, table=True):
    __tablename__ = "transaction_tag"

    id: int = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transaction.id")
    tag_id: int = Field(foreign_key="tag.id")


class TransactionDefault(BaseSQLModel):
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: Decimal = Field(decimal_places=2, max_digits=10)
    date: datetime
    description: str | None = None


class Transaction(TransactionDefault, table=True):
    id: int = Field(default=None, primary_key=True)

    user: "User" = Relationship(back_populates="transactions")  # noqa: F821
    category: "Category" = Relationship(back_populates="transactions")  # noqa: F821

    tags: list["Tag"] = Relationship(  # noqa: F821
        back_populates="transactions",
        link_model=TransactionTagLink,
    )


class TransactionUpdate(BaseSQLModel):
    amount: Decimal | None
    date: datetime | None
    description: str | None


class TransactionCreate(BaseSQLModel):
    user_id: int
    category_id: int
    amount: Decimal
    date: datetime
    description: str = None
    tag_ids: list[int] | None = []
