from typing import List

import aiohttp
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import MAIN_URL
from gurupod.fastguru.database import engine, get_session
from gurupod.models.episode import Episode, EpisodeDB, EpisodeOut
from gurupod.scrape import scrape_new_eps

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
async def put(episodes: list[Episode], session: Session = Depends(get_session)):
    new_eps = filter_existing(episodes, session)
    return validate_add(new_eps, session, commit=True)


@router.get('/scrape_add', response_model=List[EpisodeOut])
async def scrape_add(session: Session = Depends(get_session)):
    valid_new = await new_eps(session)

    return validate_add(valid_new, session, commit=True)



@router.get('/new_eps', response_model=List[EpisodeOut])
async def new_eps(session: Session = Depends(get_session)):
    existing_eps = set(session.exec(select(EpisodeDB.name).order_by(EpisodeDB.date)).all())
    print(f'found{len(existing_eps)} existing episodes {existing_eps[:-5:-1]}...')

    async with aiohttp.ClientSession() as aio_session:
        return await scrape_new_eps(aio_session, main_url=MAIN_URL, existing_eps=existing_eps)


def validate_add(eps: list[Episode], session, commit=False) -> List[Episode | EpisodeOut]:
    valid = [EpisodeDB.model_validate(_) for _ in eps]
    if valid:
        session.add_all(valid)
        if commit:
            session.commit()
            [session.refresh(_) for _ in valid]
    return valid or []


def filter_existing(eps: list[Episode], session) -> List[Episode]:
    exist_names = session.exec(select(EpisodeDB.name)).all()
    return [ep for ep in eps if ep.name not in exist_names]
