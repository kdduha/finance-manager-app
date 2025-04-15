from sqlmodel import Field, Relationship
from datetime import datetime
from decimal import Decimal
from src.schemas.base import BaseSQLModel
from src.schemas.transactions import TransactionTagLink


class TagDefault(BaseSQLModel):
    name: str
    user_id: int = Field(foreign_key="user.id")


class Tag(TagDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="tags")

    transactions: list["Transaction"] = Relationship(
        back_populates="tags",
        link_model=TransactionTagLink,
    )


class TagUpdate(BaseSQLModel):
    name: str | None = None


class TransactionWithTags(BaseSQLModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    date: datetime
    description: str | None = None
    tags: list[Tag]
