from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import REDDIT_SUB_KEY
from gurupod.fastguru.database import engine, get_session
from gurupod.models.episode import EpisodeDB, EpisodeIn, EpisodeOut
from gurupod.redditguru.reddit import submit_episiode

router = APIRouter()


@router.get("/{ep_id}", response_model=EpisodeOut)
def read_one(ep_id: int):
    with Session(engine) as session:
        return session.get(EpisodeDB, ep_id)


@router.get("/", response_model=List[EpisodeOut])
def read_all():
    with Session(engine) as session:
        return session.exec(select(EpisodeDB)).all()


@router.post("/put/", response_model=List[EpisodeOut])
async def put(episodes: list[EpisodeIn], session: Session = Depends(get_session)):
    unique_eps = filter_existing(episodes, session)
    if validated := [EpisodeDB.model_validate(episode) for episode in unique_eps]:
        for ep in validated:
            session.add(ep)
        session.commit()
        [session.refresh(valid) for valid in validated]
        return validated


@router.get('/check_new_eps')
async def check_new_eps(session: Session = Depends(get_session)):
    new_eps = await new_episodes_()
    return new_eps


@router.get('/new_episode_reddit/{key}/{ep_id}')
async def post_episode_reddit(key, ep_id, session: Session = Depends(get_session)):
    if key != REDDIT_SUB_KEY:
        return 'wrong key'
    episode = session.get(EpisodeDB, ep_id)

    return submit_episiode(episode)


def filter_existing(eps: list[EpisodeIn], session):
    exist_names = session.exec(select(EpisodeDB.name)).all()
    return [ep for ep in eps if ep.name not in exist_names]
