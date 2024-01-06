# from __future__ import annotations as _annotations

import asyncio
import sys
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from asyncpraw import Reddit
from backupbot.pruner import Pruner
from episode_scraper.episode_bot import EpisodeBot
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastui import prebuilt_html
from fastui.dev import dev_fastapi_app
from sqlmodel import Session
from backupbot import BackupBot
from gurupod.core.consts import (
    BACKUP_JSON,
    BACKUP_SLEEP,
    INITIALIZE,
    LOG_PATH,
    MAIN_URL,
    RUN_BACKUP_BOT,
    RUN_EP_BOT,
    RUN_SUB_BOT,
    logger,
    param_log_strs,
)
from gurupod.core.logger_config import get_logger

from episode_scraper import Episode
from gurupod.models.guru import Guru
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink, RedditThreadGuruLink

from redditbot import RedditThread

# from gurupod.reddit_monitor.subreddit_bot import SubredditMonitor
from redditbot import SubredditMonitor
from gurupod.core.database import create_db, engine_
from gurupod.reddit_monitor.managers import reddit_cm
from gurupod.routers.auth import router as auth_router
from gurupod.routers.components_list import router as components_router
from gurupod.routers.forms import router as forms_router
from gurupod.routers.main import router as main_router
from gurupod.routers.guroute import router as guru_router
from gurupod.routers.eps import router as eps_router
from gurupod.routers.red import router as red_router

frontend_reload = "--reload" in sys.argv

JSON_NAMES_TO_MODEL_MAP = {
    "episode": Episode,
    "guru": Guru,
    "reddit_thread": RedditThread,
    "guru_ep_link": GuruEpisodeLink,
    "reddit_thread_episode_link": RedditThreadEpisodeLink,
    "reddit_thread_guru_link": RedditThreadGuruLink,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loading with params: {param_log_strs()}", bot_name="BOOT")
    create_db()
    logger.info("tables created", bot_name="BOOT")
    with Session(engine_()) as session:
        async with ClientSession() as aio_session:
            async with reddit_cm() as reddit:
                tasks = await bot_tasks(session, aio_session, reddit)
                yield
                logger.info("Shutting down")

                for task in tasks:
                    task.cancel()

                await asyncio.gather(*tasks, return_exceptions=True)
                if RUN_BACKUP_BOT:
                    await BackupBot(session, JSON_NAMES_TO_MODEL_MAP, BACKUP_JSON).backup()


if frontend_reload:
    app = dev_fastapi_app(lifespan=lifespan)
else:
    app = FastAPI(lifespan=lifespan)

app.include_router(components_router, prefix="/api/components")
app.include_router(forms_router, prefix="/api/forms")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(guru_router, prefix="/api/guru")
app.include_router(eps_router, prefix="/api/eps")
app.include_router(red_router, prefix="/api/red")
app.include_router(main_router, prefix="/api")


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt() -> str:
    return "User-agent: *\nAllow: /"


@app.get("/favicon.ico", status_code=404, response_class=PlainTextResponse)
async def favicon_ico() -> str:
    return "page not found"


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="DecodeTheBot"))


async def bot_tasks(session: Session, aio_session: ClientSession, reddit: Reddit):
    tasks = []
    try:
        if RUN_EP_BOT:
            ep_bot = await EpisodeBot.from_url(session, aio_session, MAIN_URL)
            tasks.append(asyncio.create_task(ep_bot.run()))
    except Exception as e:
        logger.error(f"Error initiating EpisodeBot: {e}")

    try:
        if RUN_BACKUP_BOT or INITIALIZE:
            back_bot = BackupBot(
                session=session,
                json_name_to_model_map=JSON_NAMES_TO_MODEL_MAP,
                backup_target=BACKUP_JSON,
            )
            pruner = Pruner(backup_target=BACKUP_JSON)
            if INITIALIZE:
                back_bot.restore()
            if RUN_BACKUP_BOT:
                tasks.append(asyncio.create_task(backup_tasks(back_bot, pruner)))
    except Exception as e:
        logger.error(f"Error initiating backup_bot: {e}")

    try:
        if RUN_SUB_BOT:
            sub_bot = await SubredditMonitor.run(session, reddit)
            tasks.append(asyncio.create_task(sub_bot.monitor()))
    except Exception as e:
        logger.error(f"Error initiating SubredditMonitor: {e}")

    return tasks


async def backup_tasks(backupbot: BackupBot, pruner: Pruner):
    await backupbot.backup()
    await pruner.copy_and_prune()


## vaguely neater but dont get separate error handling for launching each bot....
# async def bot_tasks(session: Session, aio_session: ClientSession, reddit: Reddit):
#     bots = []
#     try:
#         if RUN_EP_BOT:
#             bots.append(await EpisodeBot.from_config(session, aio_session, reddit))
#     except Exception as e:
#         logger.error(f"Error initiating EpisodeBot: {e}")
#
#     try:
#         if RUN_BACKUP_BOT:
#             bots.append(BackupBot(session, BACKUP_JSON))
#     except Exception as e:
#         logger.error(f"Error initiating backup_bot: {e}")
#
#     try:
#         if RUN_SUB_BOT:
#             bots.append(await SubredditMonitor.run(session, reddit))
#     except Exception as e:
#         logger.error(f"Error initiating SubredditMonitor: {e}")
#
#     try:
#         return [asyncio.create_task(bot.run()) for bot in bots]
#     except Exception as e:
#         logger.error(f"Error running bot tasks {e}")
