import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import EPISODES_MOD, MONITOR_SUB, TEST_SUB, THREADS_JSON
from data.gurunames import GURUS
from gurupod.database import create_db_and_tables, engine_
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode
from gurupod.models.guru import Guru
from gurupod.models.responses import EpisodeWith
from gurupod.redditbot.managers import reddit_cm
from gurupod.routing.episode_funcs import log_episodes, remove_existing
from gurupod.routing.episode_routes import ep_router, fetch, put_ep
from gurupod.redditbot.monitor import SubredditMonitor
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

        async with reddit_cm() as reddit:
            tasks = []
            episode_monitor_task = asyncio.create_task(run_periodic_task(session, check_new_ep, reddit, 1))
            tasks.append(episode_monitor_task)
            # tasks = [asyncio.create_task(run_periodic_task(reddit, 10))]

            if MONITOR_SUB:
                subreddit = await reddit.subreddit(TEST_SUB)
                sub_bot = SubredditMonitor(session, subreddit)
                await sub_bot.monitor()

        await asyncio.gather(*tasks, return_exceptions=True)

    yield

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


def reddit_msg_from_ep(submission, episode: Episode):
    msg = f"""
    New episode {episode.title} scraped from Captivate
    posted in testsub: {submission.shortlink}
    """
    return msg


async def run_periodic_task(session, func, reddit, interval):
    while True:
        await func(session, reddit)
        await asyncio.sleep(interval)


async def check_new_ep(session, reddit):
    if neweps := await fetch(session=session):
        for ep in neweps:
            logger.info(f"Fetched new episode: {ep}")
            # submitted = await submit_episode_subreddit(ep, TEST_SUB)
            # await message_home(reddit, reddit_msg_from_ep(submitted, ep))


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
