import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info
from sqlalchemy.future import select

from graphql_parser.models import User, Transaction


@strawberry.type
class TransactionType:
    id: int
    amount: float
    date: str
    description: str


@strawberry.type
class UserType:
    id: int
    username: str
    email: str

    @strawberry.field
    async def transactions(self, info: Info) -> list[TransactionType]:
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Transaction).where(Transaction.user_id == self.id))
        transactions = result.scalars().all()  # <-- FIX
        return [
            TransactionType(
                id=t.id,
                amount=float(t.amount),
                date=str(t.date),
                description=t.description or ""
            )
            for t in transactions
        ]


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info: Info) -> list[UserType]:
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(User))
        users = result.scalars().all()  # <-- FIX
        return [
            UserType(
                id=u.id,
                username=u.username,
                email=u.email
            )
            for u in users
        ]

    @strawberry.field
    async def transactions(self, info: Info) -> list[TransactionType]:
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(Transaction))
        transactions = result.scalars().all()  # <-- FIX
        return [
            TransactionType(
                id=t.id,
                amount=float(t.amount),
                date=str(t.date),
                description=t.description or ""
            )
            for t in transactions
        ]

    @strawberry.field
    async def user_by_id(self, info: Info, id: int) -> UserType | None:
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()  # <-- OK as-is
        if user:
            return UserType(
                id=user.id,
                username=user.username,
                email=user.email
            )
        return None
