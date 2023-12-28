import asyncio
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from fastapi import FastAPI
from sqlmodel import Session

from data.consts import (
    BACKUP_JSON,
    BACKUP_SLEEP,
    EPISODE_MONITOR_SLEEP,
    INITIALIZE,
    RUN_BACKUP_BOT,
    RUN_EP_BOT,
    RUN_SUB_BOT,
    SUB_IN_USE,
    MAIN_URL,
)
from gurupod.episodebot.episode_monitor import EpisodeBot
from gurupod.database import create_db_and_tables, engine_
from gurupod.gurulog import get_logger
from gurupod.redditbot.managers import reddit_cm
from gurupod.routes import ep_router
from gurupod.redditbot.subred_monitor import subreddit_bot
from gurupod.backup_bot import backup_bot, db_to_json, get_dated_filename, gurus_from_file

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    logger.info("tables created")
    with Session(engine_()) as session:
        if INITIALIZE:
            gu = await gurus_from_file(session)
            # db_from_json(session, BACKUP_JSON)
        async with ClientSession() as aio_session:
            async with reddit_cm() as reddit:
                tasks = await bot_tasks(session, aio_session, reddit, SUB_IN_USE)
                yield
                logger.info("Shutting down")

                for task in tasks:
                    task.cancel()

                await asyncio.gather(*tasks, return_exceptions=True)
                dated_filename = get_dated_filename(BACKUP_JSON)
                await db_to_json(session, dated_filename)


async def bot_tasks(session, aio_session, reddit, sub_name):
    try:
        subreddit = await reddit.subreddit(sub_name)
        recipient = await reddit.redditor("decodethebot", fetch=False)
        tasks = []
        if RUN_EP_BOT:
            ep_bot = EpisodeBot(session, aio_session, subreddit, EPISODE_MONITOR_SLEEP, recipient, MAIN_URL)
            tasks.append(
                asyncio.create_task(ep_bot.wake())
                # asyncio.create_task(episode_bot(session, aio_session, subreddit, EPISODE_MONITOR_SLEEP, recipient))
            )
        if RUN_BACKUP_BOT:
            tasks.append(asyncio.create_task(backup_bot(session, BACKUP_SLEEP)))
        if RUN_SUB_BOT:
            tasks.append(asyncio.create_task(subreddit_bot(session, subreddit)))
        return tasks
    except Exception as e:
        logger.error(f"Error in monitor_tasks: {e}")
        ...


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
