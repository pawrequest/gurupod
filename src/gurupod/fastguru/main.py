import copy
import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI
from sqlmodel import SQLModel, Session, create_engine, select

from data.consts import EPISODES_JSON, GURU_DB
from gurupod.models.episode import Episode, EpisodeCreate, EpisodeRead

sqlite_file_name = GURU_DB
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/ep_from_url/", response_model=EpisodeRead)
async def ep_from_name_url(episode: EpisodeCreate, session: Session = Depends(get_session)):
    """ requires name and url"""
    try:
        await episode.get_data()

        db_ep = Episode.model_validate(episode)
        session.add(db_ep)
        session.commit()
        session.refresh(db_ep)
        return db_ep
    except Exception as e:
        print(e)
        session.rollback()
        return f'FAILED TO ADD EPISODE {episode.name}\nERROR:{e}'


@app.get("/eps/", response_model=List[EpisodeRead])
def read_episodes():
    with Session(engine) as session:
        episodes = session.exec(select(Episode)).all()
        return episodes






@app.post("/json_in/")
async def json_in(epsdict: dict, session: Session = Depends(get_session)):
    exist = session.query(Episode).all()
    exists = {e.name for e in exist}
    new_eps_in = [(name, ep) for name, ep in epsdict.items() if name not in exists]

    for name, ep in new_eps_in:
        try:
            ep_ob = Episode(name=name,
                            url=ep['show_url'],
                            notes='\n'.join(ep['show_notes']),
                            links=ep['show_links'],
                            date_published=datetime.strptime(ep['show_date'], '%Y-%m-%d')
                            )
            db_ep = Episode.model_validate(ep_ob)
            session.add(db_ep)
        except Exception:
            ...

    if session.dirty or session.new or session.deleted:
        try:
            new_made = copy.deepcopy(session.new)
            session.commit()
            return [e for e in new_made]
        except Exception as e:
            print(e)
            session.rollback()
    else:
        return 'NO CHANGES'
