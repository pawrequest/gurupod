from typing import List

import aiohttp
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import MAIN_URL, REDDIT_SUB_KEY
from gurupod.fastguru.database import engine, get_session
from gurupod.models.episode import EpisodeDB, EpisodeIn, EpisodeOut
from gurupod.redditguru.reddit import submit_episiode
from gurupod.scrape import parse_main_page

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
    new_eps = filter_existing(episodes, session)
    if valid := [EpisodeDB.model_validate(episode) for episode in new_eps]:
        session.add_all(valid)
        session.commit()
        [session.refresh(_) for _ in valid]
        return valid


@router.get('/check_new_eps', response_model=List[EpisodeOut])
async def check_new_eps(session: Session = Depends(get_session)):
    existing_eps = session.exec(select(EpisodeDB.name)).all()
    print(f'found{len(existing_eps)} episodes {existing_eps[:5:-1]}')
    async with aiohttp.ClientSession() as aio_session:
        epis = await parse_main_page(aio_session, main_url=MAIN_URL, existing_eps=existing_eps)

        if valid := [EpisodeDB.model_validate(_) for _ in epis]:
            session.add_all(valid)
            session.commit()
            [session.refresh(_) for _ in valid]
            return valid

        else:
            return []


@router.get('/new_episode_reddit/{key}/{ep_id}')
async def post_episode_reddit(key, ep_id, session: Session = Depends(get_session)):
    if key != REDDIT_SUB_KEY:
        return 'wrong key'
    episode = session.get(EpisodeDB, ep_id)

    return submit_episiode(episode)


def filter_existing(eps: list[EpisodeIn], session):
    exist_names = session.exec(select(EpisodeDB.name)).all()
    return [ep for ep in eps if ep.name not in exist_names]
