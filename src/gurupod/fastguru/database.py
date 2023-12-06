from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from data.consts import GURU_DB

sqlite_url = f"sqlite:///{GURU_DB}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


