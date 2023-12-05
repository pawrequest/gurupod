
from typing import Union

from fastapi import FastAPI
from sqlmodel import SQLModel, Session, create_engine

from data.consts import EPISODES_JSON, MAIN_URL
from gurupod import fetch_episodes

app = FastAPI()
engine = create_engine("sqlite:///episodes.db")


def pop_from_json(infile):
    episodes = fetch_episodes(main_url=MAIN_URL, injson=infile)
    with Session(engine) as session:
        [session.add(episode) for episode in episodes]
        session.commit()


pop_from_json(EPISODES_JSON)
SQLModel.metadata.create_all(engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# class Hero(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     secret_name: str
#     age: Optional[int] = None
#
#
# def add_hero(hero: Hero):
#     heros = [Hero(name="Deadpond", secret_name="Dive Wilson"),
#              Hero(name="Spider-Boy", secret_name="Pedro Parqueador"),
#              Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)]
#
#     with Session(engine) as session:
#         session.add(heros)
#         session.commit()
#


# with Session(engine) as session:
#     session.add(hero_1)
#     session.add(hero_2)
#     session.add(hero_3)
#     session.commit()
