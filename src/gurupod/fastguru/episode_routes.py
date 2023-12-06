from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import REDDIT_SUB_KEY
from gurupod.fastguru.database import engine, get_session
from gurupod.models.episode_new import Episode, EpisodeCreate, EpisodeRead
from gurupod.redditguru.reddit import submit_episiode

router = APIRouter()


@router.get("/{ep_id}", response_model=EpisodeRead)
def read_one(ep_id: int):
    with Session(engine) as session:
        return session.get(Episode, ep_id)


@router.get("/", response_model=List[EpisodeRead])
def read_all():
    with Session(engine) as session:
        return session.exec(select(Episode)).all()


@router.post("/put/", response_model=List[EpisodeRead])
async def put(episodes: list[EpisodeCreate], session: Session = Depends(get_session)):
    unique_eps = await filter_existing(episodes, session)
    episodes_o = [await _ep_in(ep, session) for ep in unique_eps]
    validated = [Episode.model_validate(episode) for episode in episodes_o]
    for ep in validated:
        session.add(ep)
    if validated:
        session.commit()
        [session.refresh(valid) for valid in validated]
    return validated

@router.get('/new_episode_reddit/{key}/{ep_id}')
async def post_episode_reddit(key, ep_id, session: Session = Depends(get_session)):
    if key != REDDIT_SUB_KEY:
        return 'wrong key'
    episode = session.get(Episode, ep_id)

    return submit_episiode(episode)




async def _ep_in(ep: EpisodeCreate, session: Session = Depends(get_session)):
    if all([ep.notes, ep.links, ep.date]):
        epi = ep
    else:
        epi = await Episode.ep_scraped(ep.name, ep.url)
    return epi



async def filter_existing(eps: list[EpisodeCreate], session):
    exist_names = session.exec(select(Episode.name)).all()
    return [ep for ep in eps if ep.name not in exist_names]
