import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import MONITOR_SUB, SUB_IN_USE
from episode_monitor import episode_monitor
from gurupod.database import create_db_and_tables, engine_
from gurupod.gurulog import get_logger
from gurupod.redditbot.managers import reddit_cm
from gurupod.routing.episode_routes import ep_router
from gurupod.redditbot.monitor import SubredditMonitor
from initialise import episodes_to_json, gurus_from_file

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    sub_name = SUB_IN_USE
    create_db_and_tables()
    logger.debug("tables created")
    with Session(engine_()) as session:
        await gurus_from_file(session)
        # await eps_from_file(session)

        async with reddit_cm() as reddit:
            ep_monitor = await monitor_tasks(reddit, session, sub_name)
            yield

            ep_monitor.cancel()
            await ep_monitor
            await episodes_to_json(session)


async def monitor_tasks(reddit, session, sub_name):
    subreddit = await reddit.subreddit(sub_name)
    recipient = await reddit.redditor("decodethebot", fetch=False)
    ep_monitor = asyncio.create_task(episode_monitor(session, subreddit, 60 * 60, recipient))
    if MONITOR_SUB:
        sub_bot = SubredditMonitor(session, subreddit)
        await sub_bot.monitor()
    return ep_monitor


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
