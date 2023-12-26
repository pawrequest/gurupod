import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import BACKUP_JSON, MONITOR_SUB, SUB_IN_USE, EPISODE_MONITOR_SLEEP, BACKUP_SLEEP
from episode_monitor import do_backup, episode_monitor
from gurupod.database import create_db_and_tables, engine_
from gurupod.gurulog import get_logger
from gurupod.redditbot.managers import reddit_cm
from gurupod.routing.episode_routes import ep_router
from gurupod.redditbot.monitor import reddit_monitor
from initialise import db_to_json

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    sub_name = SUB_IN_USE
    create_db_and_tables()
    logger.debug("tables created")
    with Session(engine_()) as session:
        # db_from_json(session, BACKUP_JSON)

        async with reddit_cm() as reddit:
            tasks = await bot_tasks(reddit, session, sub_name)
            yield
            logger.info("Shutting down")

            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)
            await db_to_json(session, BACKUP_JSON)


async def bot_tasks(reddit, session, sub_name):
    try:
        subreddit = await reddit.subreddit(sub_name)
        recipient = await reddit.redditor("decodethebot", fetch=False)
        tasks = [
            asyncio.create_task(episode_monitor(session, subreddit, EPISODE_MONITOR_SLEEP, recipient)),
            asyncio.create_task(do_backup(session, BACKUP_SLEEP)),
        ]
        if MONITOR_SUB:
            # subreddot = SubredditMonitor(session, subreddit)
            tasks.append(asyncio.create_task(reddit_monitor(session, subreddit)))
            # await subreddot_bot.monitor()
        return tasks
    except Exception as e:
        logger.error(f"Error in monitor_tasks: {e}")
        ...


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
