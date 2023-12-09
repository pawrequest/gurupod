import itertools
from typing import List

from aiohttp import ClientSession as AioSession
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import MAIN_URL
from gurupod.fastguru.database import get_session
from gurupod.models.episode import Episode, EpisodeDB, EpisodeOut
from gurupod.scrape import scrape_new_eps_url

router = APIRouter()


@router.get("/{ep_id}", response_model=EpisodeOut)
def read_one(ep_id: int, session: Session = Depends(get_session)):
    return session.get(EpisodeDB, ep_id)


@router.get("/", response_model=List[EpisodeOut])
def read_all(session: Session = Depends(get_session)):
    return session.exec(select(EpisodeDB)).all()


@router.post("/put/", response_model=List[EpisodeOut])
async def put(episodes: list[Episode], session: Session = Depends(get_session)):
    new_eps = filter_existing_names(episodes, session)
    return validate_add(new_eps, session, commit=True)


@router.get('/fetch', response_model=List[EpisodeOut])
async def fetch_episodes(session: Session = Depends(get_session)):
    """ check captivate for new episodes and add to db"""
    if new_eps := await scrape_eps(session):
        print(f'found {len(new_eps)} new episodes: {[_.name for _ in new_eps]}')
        return validate_add(new_eps, session, commit=True)
    else:
        print('no new episodes found')
        return []


@router.get('/scrape', response_model=List[EpisodeOut])
async def scrape_eps(session: Session = Depends(get_session)):
    """ endpoint for dry-run / internal use"""
    existing_eps = await existing_urls(session)
    async with AioSession as aio_session:
        return await scrape_new_eps_url(aio_session, main_url=MAIN_URL, existing_urls=existing_eps)


async def existing_urls(session: Session):
    existing_eps = set(session.exec(select(EpisodeDB.url).order_by(EpisodeDB.date)).all())
    print(f'found{len(existing_eps)} existing episode links:')
    print('\n'.join(itertools.islice(existing_eps, 5)), '...')
    return existing_eps


def validate_add(eps: list[Episode], session: Session, commit=False) -> List[Episode | EpisodeOut]:
    valid = [EpisodeDB.model_validate(_) for _ in eps]
    if valid:
        session.add_all(valid)
        if commit:
            session.commit()
            [session.refresh(_) for _ in valid]
    return valid or []


def filter_existing_names(eps: list[Episode], session: Session) -> List[Episode]:
    exist_names = session.exec(select(EpisodeDB.name)).all()
    return [ep for ep in eps if ep.name not in exist_names]
