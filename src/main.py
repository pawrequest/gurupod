import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import EPISODES_MOD, GURU_SUB, MONITOR_SUB, THREADS_JSON, TEST_SUB
from data.gurunames import GURUS
from gurupod.database import create_db_and_tables, engine_
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode
from gurupod.models.guru import Guru
from gurupod.models.responses import EpisodeWith
from gurupod.redditbot.managers import subreddit_cm
from gurupod.routing.episode_funcs import log_episodes, remove_existing
from gurupod.routing.episode_routes import ep_router, put_ep
from gurupod.redditbot.monitor import SubredditMonitor, flair_submission, submission_to_thread
from gurupod.routing.reddit_routes import red_router

logger = get_logger()


# ...


#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.debug("Starting lifespan")
#     create_db_and_tables()
#     logger.debug("tables created")
#     with Session(engine_()) as session:
#         await import_gurus_from_file(session)
#         await eps_from_json(session)
#         if MONITOR_SUB:
#             async with subreddit_cm(TEST_SUB) as subreddit:
#                 sub_bot = SubredditMonitor(session, subreddit)
#                 await sub_bot()
#         else:
#             logger.info("No monitor")
#         yield
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan")
    create_db_and_tables()
    logger.debug("tables created")
    with Session(engine_()) as session:
        await import_gurus_from_file(session)
        await eps_from_json(session)

        tasks = [asyncio.create_task(run_periodic_task(check_new_ep, 100))]

        if MONITOR_SUB:
            async with subreddit_cm(TEST_SUB) as subreddit:
                sub_bot = SubredditMonitor(session, subreddit)
                await sub_bot.monitor()
                # sub_monitor = asyncio.create_task(sub_bot.monitor())
                # tasks.append(sub_monitor)

        yield

        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def run_periodic_task(func, interval):
    while True:
        await func()
        await asyncio.sleep(interval)


async def check_new_ep():
    logger.info("Checking for new episodes")


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
app.include_router(red_router, prefix="/red")


async def eps_from_json(session: Session) -> list[EpisodeWith]:
    with open(EPISODES_MOD, "r") as f:
        eps_j = json.load(f)
        ep_resp = await put_ep(eps_j, session)
        if new := ep_resp.episodes:
            logger.debug(f"Loading {len(new)} episodes from {EPISODES_MOD}")
            log_episodes(new)
            return new


async def threads_from_json(session: Session):
    with open(THREADS_JSON, "r") as f:
        threads_j = json.load(f)
        logger.info(f"Loading {len(threads_j)} episodes from {THREADS_JSON}")
        # added_eps = await put_ep(threads_j, session)
    # return added_eps


#
async def import_gurus_from_file(session: Session):
    if guru_names := remove_existing(GURUS, Guru.name, session):
        logger.info(f"Adding {len(guru_names)} new gurus: {guru_names}")
        new_gurus = [Guru(name=_) for _ in guru_names]
        session.add_all(new_gurus)
        session.commit()
        [session.refresh(_) for _ in new_gurus]
        return new_gurus
