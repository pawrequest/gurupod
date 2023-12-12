from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from data.consts import MAIN_URL
from gurupod.database import get_session
from gurupod.models.episode import Episode, EpisodeDB, EpisodeResponse, \
    EpisodeResponseNoDB
from gurupod.routing.route_funcs import _log_new_urls, filter_existing_url, validate_add
from gurupod.scrape import episode_scraper
from gurupod.scraper_oop import expand_and_sort

ep_router = APIRouter()


@ep_router.post("/put_ep", response_model=EpisodeResponse)
async def put_ep(episodes: list[Episode], session: Session = Depends(get_session)):
    if new_eps := filter_existing_url(episodes, session):
        _log_new_urls(new_eps)
        eps = await expand_and_sort(new_eps)
        res = validate_add(eps, session, commit=True)
        resp = EpisodeResponse.from_episodes(res)
        return resp
    else:
        resp = EpisodeResponse.no_new()
        return resp


@ep_router.get('/fetch{max_rtn}', response_model=EpisodeResponse)
async def fetch(session: Session = Depends(get_session), max_rtn=None):
    """ check captivate for new episodes and add to db"""
    scraped = await _scrape(session, max_rtn=max_rtn)
    eps = scraped.episodes
    return await put_ep(eps, session)


@ep_router.get('/scrape{max_rtn}', response_model=EpisodeResponseNoDB)
async def _scrape(session: Session = Depends(get_session), max_rtn=None):
    """ endpoint for dry-run / internal use"""
    async with ClientSession() as aio_session:
        res = await episode_scraper(session, aio_session, main_url=MAIN_URL, max_return=max_rtn)
        return EpisodeResponseNoDB.from_episodes(res)


@ep_router.get("/{ep_id}", response_model=EpisodeResponse)
def read_one(ep_id: int, session: Session = Depends(get_session)):
    episode_db = session.get(EpisodeDB, ep_id)
    if episode_db is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    elif isinstance(episode_db, EpisodeDB):
        episode_: EpisodeDB = episode_db
        return EpisodeResponse.from_episodes([episode_])
    else:
        raise HTTPException(status_code=500, detail="returned data not EpisodeDB")


@ep_router.get("/", response_model=EpisodeResponse)
def read_all(session: Session = Depends(get_session)):
    eps = session.exec(select(EpisodeDB)).all()
    return EpisodeResponse.from_episodes(list(eps))
