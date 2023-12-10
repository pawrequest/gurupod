from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session



def engine_(config=None):
    if config is None:
        from data.consts import GURU_DB
        db_url = f"sqlite:///{GURU_DB}"
        connect_args = {"check_same_thread": False}
    else:
        db_url = config['db_url']
        connect_args = config.get('connect_args', {})
    return create_engine(db_url, echo=True, connect_args=connect_args)


def get_session(engine=None) -> Session:
    if engine is None:
        engine = engine_()
    with Session(engine) as session:
        yield session
    session.close()


def create_db_and_tables(engine=None):
    if engine is None:
        engine = engine_()
    SQLModel.metadata.create_all(engine)
