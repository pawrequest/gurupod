import asyncio
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from asyncpraw import Reddit
from fastapi import FastAPI
from sqlmodel import Session

from gurupod.core.consts import (
    BACKUP_JSON,
    INITIALIZE,
    RUN_BACKUP_BOT,
    RUN_EP_BOT,
    RUN_SUB_BOT,
    param_log_strs,
)
from gurupod import EpisodeBot, SubredditMonitor
from gurupod.core.database import create_db_and_tables, engine_
from loguru import logger
from gurupod.reddit_monitor.managers import reddit_cm
from gurupod.core.routes import ep_router
from gurupod.backup_restore.backup_bot import backup_bot, db_from_json, db_to_json, gurus_from_file, BackupBot


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loading with params: {param_log_strs()}", bot_name="BOOT")
    create_db_and_tables()
    logger.info("tables created", bot_name="BOOT")
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


async def make_wiki():
    ...


async def bot_tasks(session: Session, aio_session: ClientSession, reddit: Reddit):
    tasks = []
    try:
        if RUN_EP_BOT:
            ep_bot = await EpisodeBot.from_config(session, aio_session, reddit)
            tasks.append(asyncio.create_task(ep_bot.run()))
    except Exception as e:
        logger.error(f"Error initiating EpisodeBot: {e}")

    try:
        if RUN_BACKUP_BOT:
            back_bot = BackupBot(session)
            tasks.append(asyncio.create_task(back_bot.run()))
    except Exception as e:
        logger.error(f"Error initiating backup_bot: {e}")

    try:
        if RUN_SUB_BOT:
            sub_bot = await SubredditMonitor.from_config(session, reddit)
            tasks.append(asyncio.create_task(sub_bot.monitor()))
    except Exception as e:
        logger.error(f"Error initiating SubredditMonitor: {e}")

    return tasks


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
