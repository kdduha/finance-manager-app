from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from graphql_parser.config import cfg

async_engine: AsyncEngine = create_async_engine(
    cfg.db.url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=cfg.db.debug,
)

async_session_factory = sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
