import asyncio
import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import EPISODES_MOD, GURU_SUB
from gurupod.database import create_db_and_tables, engine_
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode
from gurupod.redditbot.monitor import launch_monitor
from gurupod.routing.episode_routes import ep_router, put_ep
from gurupod.routing.reddit_routes import red_router

logger = get_logger()
monitior_sub = os.environ.get("MONITOR_SUB", False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")
    create_db_and_tables()
    with Session(engine_()) as session:
        ...
        # await populate_from_json(session)
        # await fetch(session)
        # [reddit.post_episode(_) for _ in new]
    monitor_task = asyncio.create_task(launch_monitor(subreddit_name=GURU_SUB, timeout=None))
    logger.info("Started monitor")
    yield
    monitor_task.cancel()
    await monitor_task


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
app.include_router(red_router, prefix="/red")


async def populate_from_json(session: Session):
    with open(EPISODES_MOD, "r") as f:
        eps_j = json.load(f)
        logger.info(f"\nLoading {len(eps_j)} episodes from {EPISODES_MOD}\n")
        valid = [Episode.model_validate(_) for _ in eps_j]
        added = await put_ep(valid, session)
        return added
