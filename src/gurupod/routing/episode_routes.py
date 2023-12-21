from typing import Sequence

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from data.consts import MAIN_URL
from gurupod.database import get_session
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode, EpisodeDB
from gurupod.models.responses import (
    EpisodeResponse,
    EpisodeResponseNoDB,
    repack_episodes,
)
from gurupod.routing.episode_funcs import (
    remove_existing_episodes,
    remove_existing_urls,
    validate_add,
)
from gurupod.scrape import scrape_urls
from gurupod.soup_expander import expand_and_sort

logger = get_logger()
ep_router = APIRouter()


# a decorator to log endpioint hits
def log_endpoint(func):
    async def wrapper(*args, **kwargs):
        logger.info(f"Endpoint hit: {func.__name__}")
        return await func(*args, **kwargs)

    return wrapper


@log_endpoint
@ep_router.post("/put", response_model=EpisodeResponse)
async def put_ep(
    episodes: Episode | Sequence[Episode], session: Session = Depends(get_session)
) -> EpisodeResponse:
    """add episodes to db, minimally provide {url = <url>}"""
    # logger.info(f"Endpoint hit: put_ep: {episodes}")
    new_eps = remove_existing_episodes(episodes, session)
    repacked = repack_episodes(new_eps)
    sorted = await expand_and_sort(repacked)
    res = validate_add(sorted, session, commit=True)
    resp = EpisodeResponse.from_episodes(res)
    return resp


@log_endpoint
@ep_router.get("/fetch", response_model=EpisodeResponse)
async def fetch(session: Session = Depends(get_session), max_rtn: int = None):
    """check captivate for new episodes and add to db"""
    scraped = await _scrape(session, max_rtn=max_rtn)
    eps = scraped.episodes
    return await put_ep(eps, session)


@log_endpoint
@ep_router.get("/scrape", response_model=EpisodeResponseNoDB)
async def _scrape(session: Session = Depends(get_session), max_rtn: int = None):
    """endpoint for dry-run / internal use"""
    async with ClientSession() as aio_session:
        scraped_urls = await scrape_urls(
            main_url=MAIN_URL, aiosession=aio_session, max_rtn=max_rtn
        )
        new_urls = remove_existing_urls(scraped_urls, session)
        new_eps = [Episode(url=_) for _ in new_urls]
        expanded = await expand_and_sort(new_eps)
        return EpisodeResponseNoDB.from_episodes(expanded)
        # if expanded:
        #     return EpisodeResponseNoDB.from_episodes(expanded)
        # return EpisodeResponseNoDB.empty()


@log_endpoint
@ep_router.get("/{ep_id}", response_model=EpisodeResponse)
async def read_one(ep_id: int, session: Session = Depends(get_session)):
    episode_db = session.get(EpisodeDB, ep_id)
    if episode_db is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    elif isinstance(episode_db, EpisodeDB):
        episode_: EpisodeDB = episode_db
        return EpisodeResponse.from_episodes([episode_])
    else:
        raise HTTPException(status_code=500, detail="returned data not EpisodeDB")


@log_endpoint
@ep_router.get("/", response_model=EpisodeResponse)
async def read_all(session: Session = Depends(get_session)):
    eps = session.exec(select(EpisodeDB)).all()
    return EpisodeResponse.from_episodes(list(eps))
