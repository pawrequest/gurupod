# from __future__ import annotations as _annotations

import asyncio
import sys
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from asyncpraw import Reddit
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastui import prebuilt_html
from fastui.dev import dev_fastapi_app
from sqlmodel import Session

from gurupod.core.consts import (
    BACKUP_JSON,
    INITIALIZE,
    LOG_PATH,
    RUN_BACKUP_BOT,
    RUN_EP_BOT,
    RUN_SUB_BOT,
    param_log_strs,
    logger,
)
from gurupod.core.logger_config import get_logger
from gurupod.episode_monitor.episode_bot import EpisodeBot
from gurupod.reddit_monitor.subreddit_bot import SubredditMonitor
from gurupod.core.database import create_db, engine_
from gurupod.reddit_monitor.managers import reddit_cm
from gurupod.backup_restore.backup_bot import BackupBot, db_from_json, db_to_json, gurus_from_file
from gurupod.routers.auth import router as auth_router
from gurupod.routers.components_list import router as components_router
from gurupod.routers.forms import router as forms_router
from gurupod.routers.main import router as main_router
from gurupod.routers.guroute import router as guru_router
from gurupod.routers.eps import router as eps_router
from gurupod.routers.red import router as red_router

frontend_reload = "--reload" in sys.argv


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loading with params: {param_log_strs()}", bot_name="BOOT")
    create_db()
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
            ep_bot = await EpisodeBot.from_config(session, aio_session, reddit)
            tasks.append(asyncio.create_task(ep_bot.run()))
    except Exception as e:
        logger.error(f"Error initiating EpisodeBot: {e}")

    try:
        if RUN_BACKUP_BOT:
            back_bot = BackupBot(session)
            tasks.append(asyncio.create_task(back_bot.run(backup_path=BACKUP_JSON)))
    except Exception as e:
        logger.error(f"Error initiating backup_bot: {e}")

    try:
        if RUN_SUB_BOT:
            sub_bot = await SubredditMonitor.from_config(session, reddit)
            tasks.append(asyncio.create_task(sub_bot.monitor()))
    except Exception as e:
        logger.error(f"Error initiating SubredditMonitor: {e}")

    return tasks
