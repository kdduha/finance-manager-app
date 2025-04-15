from sqlmodel import SQLModel, Session, create_engine

db_url = 'postgresql://kdduha@localhost/fastapi_db'
engine = create_engine(db_url, echo=True)


def init() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
