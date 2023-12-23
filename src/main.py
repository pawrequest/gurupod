import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import EPISODES_MOD, GURU_SUB, MONITOR_SUB
from data.gurunames import GURUS
from gurupod.database import create_db_and_tables, engine_
from gurupod.gurulog import get_logger
from gurupod.models.episode import EpisodeDB
from gurupod.models.guru import Guru
from gurupod.models.links import GuruEpisodeLink
from gurupod.redditbot.monitor import launch_monitor
from gurupod.routing.episode_funcs import remove_existing_smth
from gurupod.routing.episode_routes import ep_router, put_ep
from gurupod.routing.reddit_routes import red_router

logger = get_logger()


# ...


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")
    create_db_and_tables()
    gb = Guru.model_rebuild()
    eb = EpisodeDB.model_rebuild()
    lb = GuruEpisodeLink.model_rebuild()
    logger.info("tables created")
    with Session(engine_()) as session:
        gurus_added = await gurus_from_file(session)
        ...
        await eps_from_json(session)
        logger.info("json returned")
        # await gurus_from_file(session)
        # await assign_gurus(session)
        # await fetch(session)
        # [reddit.post_episode(_) for _ in new]
    if MONITOR_SUB:
        monitor_task = asyncio.create_task(launch_monitor(subreddit_name=GURU_SUB, timeout=None))
        logger.info("Started monitor")
        yield
        monitor_task.cancel()
        await monitor_task
    else:
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
app.include_router(red_router, prefix="/red")


async def eps_from_json(session: Session):
    with open(EPISODES_MOD, "r") as f:
        eps_j = json.load(f)
        logger.info(f"\nLoading {len(eps_j)} episodes from {EPISODES_MOD}\n")
        added_eps = await put_ep(eps_j, session)
    return added_eps


#
async def gurus_from_file(session: Session):
    guru_names = remove_existing_smth(GURUS, Guru.name, session)
    if new_gurus := [Guru(name=_) for _ in guru_names]:
        session.add_all(new_gurus)
        session.commit()
        [session.refresh(_) for _ in new_gurus]
    return new_gurus or None


# async def assign_gurus(session: Session):
#     gurus = session.exec(select(Guru)).all()
#     eps = session.exec(select(EpisodeDB)).all()
#     for ep in eps:
#         ep.gurus = [_ for _ in gurus if _.name in ep.title]
#         session.add(ep)
#
#     # for guru in gurus:
#     #     guru_eps = [_ for _ in eps if guru.name in _.title]
#     #     guru.episodes.extend(guru_eps)
#     #     session.add(guru)
#     session.commit()
