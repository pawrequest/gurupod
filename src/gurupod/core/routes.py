from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from gurupod.core.database import get_session
from gurupod.core.gurulog import get_logger
from gurupod.models.episode import Episode
from gurupod.models.responses import EpisodeResponse

logger = get_logger()
ep_router = APIRouter()


#
@ep_router.get("/{ep_id}", response_model=EpisodeResponse)
async def read_one(ep_id: int, session: Session = Depends(get_session)):
    episode_db = session.get(Episode, ep_id)
    if episode_db is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    elif isinstance(episode_db, Episode):
        episode_: Episode = episode_db
        return await EpisodeResponse.from_episodes([episode_])


@ep_router.get("/", response_model=EpisodeResponse)
async def read_all(session: Session = Depends(get_session)):
    eps = session.exec(select(Episode)).all()
    return await EpisodeResponse.from_episodes(eps)
