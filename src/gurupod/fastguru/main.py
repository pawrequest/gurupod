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


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/eps/", response_model=EpisodeRead)
async def create_episode(episode: EpisodeCreate):
    await episode.get_data()

    with Session(engine) as session:
        db_ep = Episode.model_validate(episode)
        session.add(db_ep)
        session.commit()
        session.refresh(db_ep)
        return db_ep


@app.get("/eps/", response_model=List[EpisodeRead])
def read_episodes():
    with Session(engine) as session:
        episodes = session.exec(select(Episode)).all()
        return episodes



def get_session():
    with Session(engine) as session:
        yield session


@app.get("/pop/")
async def populate(session: Session = Depends(get_session)):
    with open(EPISODES_JSON, "r") as f:
        epsdict = json.load(f)
    exist = session.query(Episode).all()
    exists = {e.name for e in exist}

    for name, ep in epsdict.items():
        if name in exists:
            print('ALREADY EXISTS')
            continue
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
            session.commit()
            return 'SUCCESS'
        except Exception as e:
            print(e)
            session.rollback()
    else:
        return 'NO CHANGES'
