from typing import List

from aiohttp import ClientSession
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import MAIN_URL
from gurupod.fastguru.database import get_session
from gurupod.fastguru.route_funcs import filter_existing_url, validate_add
from gurupod.models.episode import Episode, EpisodeDB, EpisodeOut
from gurupod.scrape import _scraper, maybe_expand_episode

router = APIRouter()


@router.post("/put", response_model=List[EpisodeOut])
async def put(episodes: list[Episode], session: Session = Depends(get_session)):
    # if new_eps := filter_existing_names(episodes, session):
    if new_eps := filter_existing_url(episodes, session):
        for ep in new_eps:
            await maybe_expand_episode(ep)
        new_eps = sorted(new_eps, key=lambda x: x.date)
        return validate_add(new_eps, session, commit=True)
    return []


@router.get('/fetch', response_model=List[EpisodeOut])
async def fetch_episodes_endpoint(session: Session = Depends(get_session)):
    """ check captivate for new episodes and add to db"""
    if new_eps := await scrape_eps_endpoint(session):
        print(
            f'found {len(new_eps)} new episodes to scrape: \n{"\n".join(_.name for _ in new_eps)}')
        return await put(new_eps, session)
    else:
        print('no new episodes found')
        return []


@router.get('/scrape', response_model=List[Episode])
async def scrape_eps_endpoint(session: Session = Depends(get_session)):
    """ endpoint for dry-run / internal use"""
    # existing_urls = await existing_urls_(session)
    async with ClientSession() as aio_session:
        # return await _scrape_new_eps(aio_session, main_url=MAIN_URL, existing_urls=existing_urls)
        res = await _scraper(session, aio_session, main_url=MAIN_URL)
        return res


@router.get("/{ep_id}", response_model=EpisodeOut)
def read_one(ep_id: int, session: Session = Depends(get_session)):
    return session.get(EpisodeDB, ep_id)


@router.get("/", response_model=List[EpisodeOut])
def read_all(session: Session = Depends(get_session)):
    return session.exec(select(EpisodeDB)).all()
