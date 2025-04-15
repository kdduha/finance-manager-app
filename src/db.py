from sqlmodel import SQLModel, Session, create_engine
from src.config import cfg


engine = create_engine(cfg.db.url, echo=True)


def init() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
