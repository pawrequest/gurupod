from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session


# from data.consts import GURU_DB

# SQLITE_URL = f"sqlite:///{GURU_DB}"
# CONNECT_ARGS = dict(check_same_thread=False)
#
#
# def engine_(db_url: str = SQLITE_URL, connect_args=None):
#     if connect_args is None:
#         connect_args = CONNECT_ARGS
#     return create_engine(db_url, echo=True, connect_args=connect_args)
#
#
# def get_session(engine=engine_()):
#     with Session(engine) as session:
#         yield session
#
#
# def create_db_and_tables(engine=engine_()):
#     SQLModel.metadata.create_all(engine)


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
