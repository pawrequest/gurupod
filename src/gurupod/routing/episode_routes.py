from typing import List

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from data.consts import MAIN_URL
from gurupod.database import get_session
from gurupod.models.episode import Episode, EpisodeDB, EpisodeOut, EpisodeResponse
from gurupod.routing.route_funcs import _log_new_urls, filter_existing_url, validate_add
from gurupod.scrape import episode_scraper
from gurupod.scraper_oop import expand_and_sort

ep_router = APIRouter()


@ep_router.post("/put_ep", response_model=EpisodeResponse)
async def put_ep(episodes: list[Episode], session: Session = Depends(get_session)):
    if new_eps := filter_existing_url(episodes, session):
        _log_new_urls(new_eps)
        eps = expand_and_sort(new_eps)
        res:List[Episode] = validate_add(eps, session, commit=True)
        resp = EpisodeResponse.from_episodes(res)
        return resp
    else:
        resp = EpisodeResponse.no_new()
        return resp


#
# @ep_router.post("/put_ep", response_model=List[EpisodeOut])
# async def put_ep(episodes: list[Episode], session: Session = Depends(get_session)):
#     if new_eps := filter_existing_url(episodes, session):
#         for ep in new_eps:
#             await maybe_expand_episode(ep)
#         new_eps = sorted(new_eps, key=lambda x: x.date)
#         return validate_add(new_eps, session, commit=True)
#     else:
#         return []


@ep_router.get('/fetch{max_rtn}', response_model=List[EpisodeOut])
async def fetch(session: Session = Depends(get_session), max_rtn=None):
    """ check captivate for new episodes and add to db"""
    if new_eps := await _scrape(session, max_rtn=max_rtn):
        print(
            f'found {len(new_eps)} new episodes to scrape: \n{"\n".join(_.name for _ in new_eps)}')
        return await put_ep(new_eps, session)
    else:
        print('no new episodes found')
        return []


@ep_router.get('/scrape{max_rtn}', response_model=List[Episode])
async def _scrape(session: Session = Depends(get_session), max_rtn=None):
    """ endpoint for dry-run / internal use"""
    # existing_urls = await existing_urls_(session)
    async with ClientSession() as aio_session:
        # return await _scrape_new_eps(aio_session, main_url=MAIN_URL, existing_urls=existing_urls)
        res = await episode_scraper(session, aio_session, main_url=MAIN_URL, max_return=max_rtn)
        return res


@ep_router.get("/{ep_id}", response_model=EpisodeOut)
def read_one(ep_id: int, session: Session = Depends(get_session)):
    episode_db = session.get(EpisodeDB, ep_id)
    if episode_db is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode_db


@ep_router.get("/", response_model=List[EpisodeOut])
def read_all(session: Session = Depends(get_session)):
    return session.exec(select(EpisodeDB)).all()
