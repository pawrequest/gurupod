import secrets

from fastapi import Depends
from sqlmodel import Session

from .core.database import get_session
from gurupod.models.user import User


async def get_user_db(token: str, session: Session = Depends(get_session)) -> User | None:
    rs = await session.execute("select * from users where token = ?", (token,))
    if rs.rows:
        await session.execute("update users set last_active = current_timestamp where token = ?", (token,))
        return User(*rs.rows[0])


async def create_user(email: str) -> str:
    async with get_session() as session:
        token = secrets.token_hex()
        user = User(token=token, email=email)
        session.add(user)
        session.commit()
        return token


# async def delete_user(user: User) -> None:
#     async with get_session() as session:
#         await session.execute('delete from users where token = ?', (user.token,))


# async def count_users() -> int:
#     async with get_session() as session:
#         await _delete_old_users(session)
#         rs = await session.execute('select count(*) from users')
#         return rs.rows[0][0]
#

# async def create_db() -> None:
#     async with get_session() as session:
#         rs = await session.execute(
#             "select 1 from sqlite_master where type='table' and name='users'")
#         if not rs.rows:
#             await session.execute(USER_SCHEMA)


# USER_SCHEMA = """
# create table if not exists users (
#     token varchar(255) primary key,
#     email varchar(255) not null unique,
#     last_active timestamp not null default current_timestamp
# );
# """


# async def _delete_old_users(session: Session) -> None:
#     await session.execute(
#         'delete from users where last_active < datetime(current_timestamp, "-1 hour")')

# @asynccontextmanager
# async def _sessionect() -> Session:
#     # auth_token = os.getenv('SQLITE_AUTH_TOKEN')
#     # if auth_token:
#     #     url = 'libsql://fastui-samuelcolvin.turso.io'
#     # else:
#     #     url = 'file:users.db'
#     # async with libsql_client.create_client(url, auth_token=auth_token) as session:
#     #     yield session
#     url = f"sqlite:///{GURU_DB}"
#
#     # url = 'file:users.db'
#     async with libsql_client.create_client(url) as session:
#         yield session
