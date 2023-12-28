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
    MAIN_URL,
    RUN_BACKUP_BOT,
    RUN_EP_BOT,
    RUN_SUB_BOT,
    SUB_IN_USE,
)
from gurupod.podcast_monitor.podcast_bot import EpisodeBot
from gurupod.database import create_db_and_tables, engine_
from gurupod.podcast_monitor.soups import MainSoup
from gurupod.gurulog import get_logger
from gurupod.reddit_monitor.managers import reddit_cm
from gurupod.routes import ep_router
from gurupod.reddit_monitor.subreddit_bot import SubredditBot
from gurupod.backup_bot import backup_bot, db_from_json, db_to_json, get_dated_filename

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    logger.info("tables created")
    with Session(engine_()) as session:
        if INITIALIZE:
            db_from_json(session, BACKUP_JSON)
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
            mainsoup = await MainSoup.from_url(MAIN_URL, aio_session)
            ep_bot = EpisodeBot(session, aio_session, subreddit, EPISODE_MONITOR_SLEEP, recipient, mainsoup)
            tasks.append(
                asyncio.create_task(ep_bot.run())
                # asyncio.create_task(episode_bot(session, aio_session, subreddit, EPISODE_MONITOR_SLEEP, recipient))
            )
        if RUN_BACKUP_BOT:
            tasks.append(asyncio.create_task(backup_bot(session, BACKUP_SLEEP)))
        if RUN_SUB_BOT:
            sub_bot = SubredditBot(session, subreddit)
            tasks.append(asyncio.create_task(sub_bot.monitor()))
        return tasks
    except Exception as e:
        logger.error(f"Error in monitor_tasks: {e}")
        ...


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
