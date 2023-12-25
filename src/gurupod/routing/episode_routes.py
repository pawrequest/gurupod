from __future__ import annotations

from typing import Sequence

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from gurupod.database import get_session
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.models.guru import Guru
from gurupod.models.responses import (
    EpisodeResponse,
    EpisodeResponseNoDB,
    repack_validate,
)
from gurupod.routing.episode_funcs import remove_existing_episodes, scrape_and_filter, validate_add
from gurupod.soup_expander import expand_and_sort, expand_episode

logger = get_logger()
ep_router = APIRouter()


@ep_router.post("/put", response_model=EpisodeResponse)
async def put_ep(
    episodes: EpisodeBase | Sequence[EpisodeBase], session: Session = Depends(get_session)
) -> EpisodeResponse:
    """add episodes to db, minimally provide {url = <url>}"""
    if not episodes:
        return EpisodeResponse.empty()
    episodes = repack_validate(episodes)
    episodes = remove_existing_episodes(episodes, session)
    if not episodes:
        return EpisodeResponse.empty()
    episodes = await expand_and_sort(episodes)
    addepisodes = validate_add(episodes, session, commit=True)
    await assign_gurus(addepisodes, session)
    resp = EpisodeResponse.from_episodes(addepisodes)
    return resp


@ep_router.get("/fetch", response_model=EpisodeResponse)
async def fetch(session: Session = Depends(get_session), max_rtn: int = None):
    """check captivate for new episodes and add to db"""
    scraped = await _scrape(session, max_rtn=max_rtn)
    eps = scraped.episodes
    res = await put_ep(eps, session)
    return res


@ep_router.get("/scrape", response_model=EpisodeResponseNoDB)
async def _scrape(session: Session = Depends(get_session), max_rtn: int = None):
    """endpoint for dry-run / internal use"""
    async with ClientSession() as aio_session:
        out_eps = []
        async for ep in scrape_and_filter(aio_session, session):
            exp = await expand_episode(ep)
            out_eps.append(exp)
        resp = EpisodeResponseNoDB.from_episodes(out_eps)
        return resp


@ep_router.get("/{ep_id}", response_model=EpisodeResponse)
async def read_one(ep_id: int, session: Session = Depends(get_session)):
    episode_db = session.get(Episode, ep_id)
    if episode_db is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    elif isinstance(episode_db, Episode):
        episode_: Episode = episode_db
        return EpisodeResponse.from_episodes([episode_])
    else:
        raise HTTPException(status_code=500, detail="returned data not EpisodeDB")


@ep_router.get("/", response_model=EpisodeResponse)
async def read_all(session: Session = Depends(get_session)):
    eps = session.exec(select(Episode)).all()
    return EpisodeResponse.from_episodes(list(eps))


HAS_GURUS = ""


async def assign_gurus(to_assign: Sequence, session: Session):
    gurus = session.exec(select(Guru)).all()
    if not to_assign:
        return to_assign
    for target in to_assign:
        title_gurus = [_ for _ in gurus if _.name in target.title]
        target.gurus.extend(title_gurus)
        session.add(target)
    session.commit()
    [session.refresh(_) for _ in to_assign]
    return to_assign
