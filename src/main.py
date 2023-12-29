import asyncio
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from asyncpraw import Reddit
from fastapi import FastAPI
from sqlmodel import Session

from gurupod.core.consts import (
    BACKUP_JSON,
    DM_ADDRESS,
    INITIALIZE,
    MAIN_URL,
    SUB_TO_MONITOR,
    RUN_BACKUP_BOT,
    RUN_EP_BOT,
    RUN_SUB_BOT,
    WIKI_TO_WRITE,
    SUB_TO_POST,
    SUB_TO_WIKI,
    param_log_strs,
)
from gurupod import EpisodeBot, SubredditMonitor
from gurupod.core.database import create_db_and_tables, engine_
from gurupod.episode_monitor.soups import MainSoup
from gurupod.core.gurulogging import get_logger
from gurupod.reddit_monitor.managers import reddit_cm
from gurupod.core.routes import ep_router
from gurupod.backup_restore.backup_bot import backup_bot, db_from_json, db_to_json, gurus_from_file

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.warning(f"Loading with params:\n{'\n'.join(param_log_strs())}")
    create_db_and_tables()
    logger.info("tables created")
    with Session(engine_()) as session:
        if INITIALIZE:
            gurus_from_file(session)
            db_from_json(session, BACKUP_JSON)
        async with ClientSession() as aio_session:
            async with reddit_cm() as reddit:
                tasks = await bot_tasks(session, aio_session, reddit)
                yield
                logger.info("Shutting down")

                for task in tasks:
                    task.cancel()

                await asyncio.gather(*tasks, return_exceptions=True)
                if RUN_BACKUP_BOT:
                    await db_to_json(session, BACKUP_JSON)


async def bot_tasks(session: Session, aio_session: ClientSession, reddit: Reddit):
    try:
        tasks = []

        if RUN_EP_BOT:
            sub_to_post = await reddit.subreddit(SUB_TO_POST)
            sub_to_update_wiki = await reddit.subreddit(SUB_TO_WIKI)
            wiki = await sub_to_update_wiki.wiki.get_page(WIKI_TO_WRITE)
            recipient = await reddit.redditor(DM_ADDRESS, fetch=False)
            mainsoup = await MainSoup.from_url(MAIN_URL, aio_session)
            ep_bot = EpisodeBot(session, aio_session, sub_to_post, recipient, mainsoup, wiki)
            tasks.append(asyncio.create_task(ep_bot.run()))

        if RUN_BACKUP_BOT:
            tasks.append(asyncio.create_task(backup_bot(session)))

        if RUN_SUB_BOT:
            sub_to_monitor = await reddit.subreddit(SUB_TO_MONITOR)
            sub_bot = SubredditMonitor(session, sub_to_monitor)
            tasks.append(asyncio.create_task(sub_bot.monitor()))

        return tasks
    except Exception as e:
        logger.error(f"Error in monitor_tasks: {e}")
        ...


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
