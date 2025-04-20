from sqlmodel import Session, SQLModel, create_engine

from src.config import cfg
from src.schemas.users import User

engine = create_engine(cfg.db.url, echo=cfg.db.debug)


def init() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


def find_user(email: str) -> User | None:
    with Session(engine) as session:
        return session.query(User).filter(User.email == email).first()
