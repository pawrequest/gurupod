from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from gurupod.database import get_session
from gurupod.gurulog import get_logger
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
        return await EpisodeResponse.from_episodes_seq([episode_])
        # return EpisodeResponse.from_episodes([episode_])
    else:
        raise HTTPException(status_code=500, detail="returned data not EpisodeDB")


@ep_router.get("/", response_model=EpisodeResponse)
async def read_all(session: Session = Depends(get_session)):
    eps = session.exec(select(Episode)).all()
    # return EpisodeResponse.from_episodes(list(eps))
    return await EpisodeResponse.from_episodes_seq(eps)


# async def assign_gurus(to_assign: Sequence, session: Session):
#     gurus = session.exec(select(Guru)).all()
#     if not to_assign:
#         return to_assign
#     for target in to_assign:
#         title_gurus = [_ for _ in gurus if _.name in target.title]
#         target.gurus.extend(title_gurus)
#         session.add(target)
#     session.commit()
#     [session.refresh(_) for _ in to_assign]
#     return to_assign


# async def assign_tags_gen(to_assign: AsyncGenerator[Episode, None], session: Session) -> AsyncGenerator[Episode, None]:
#     tags = set(session.exec(select(Guru.name)).all())
#     async for target in to_assign:
#         if title_gurus := [_ for _ in tags if _ in target.title]:
#             target.gurus.extend(title_gurus)
#             session.add(target)
#             yield target
