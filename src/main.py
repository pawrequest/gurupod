import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import EPISODES_MOD, GURU_SUB, MONITOR_SUB, THREADS_JSON
from data.gurunames import GURUS
from gurupod.database import create_db_and_tables, engine_
from gurupod.gurulog import get_logger
from gurupod.models.guru import Guru
from gurupod.redditbot.monitor import submission_monitor
from gurupod.routing.episode_funcs import remove_existing_smth
from gurupod.routing.episode_routes import ep_router, put_ep
from gurupod.routing.reddit_routes import red_router, save_submission

logger = get_logger()


# ...


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")
    create_db_and_tables()
    logger.info("tables created")
    with Session(engine_()) as session:
        gurus_added = await import_gurus_from_file(session)
        await eps_from_json(session)
        logger.info("json returned")
        # await gurus_from_file(session)
        # await fetch(session)
        # [reddit.post_episode(_) for _ in new]
    if not MONITOR_SUB:
        logger.info("No monitor")
        yield
    else:
        async for sub in submission_monitor(subreddit_name=GURU_SUB):
            logger.info(f"Got submission: {sub}")
            await save_submission(session, sub)
            yield
        #
        # monitor_task = asyncio.create_task(
        #     launch_monitor(subreddit_name=TEST_SUB, serialised_sub_q=submission_queue, timeout=None)
        # )
        # while not submission_queue.empty():
        #     submission_data = await submission_queue.get()
        #     logger.info(f"Got submission: {submission_data}")
        #     await save_submission(session, submission_data)
        #     submission_queue.task_done()

        # logger.info("Started monitor")
        # yield
        # monitor_task.cancel()
        # await monitor_task


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
app.include_router(red_router, prefix="/red")


async def eps_from_json(session: Session):
    with open(EPISODES_MOD, "r") as f:
        eps_j = json.load(f)
        logger.info(f"\nLoading {len(eps_j)} episodes from {EPISODES_MOD}\n")
        added_eps = await put_ep(eps_j, session)
    return added_eps


async def threads_from_json(session: Session):
    with open(THREADS_JSON, "r") as f:
        threads_j = json.load(f)
        logger.info(f"\nLoading {len(threads_j)} episodes from {THREADS_JSON}\n")
        # added_eps = await put_ep(threads_j, session)
    # return added_eps


#
async def import_gurus_from_file(session: Session):
    guru_names = remove_existing_smth(GURUS, Guru.name, session)
    if new_gurus := [Guru(name=_) for _ in guru_names]:
        session.add_all(new_gurus)
        session.commit()
        [session.refresh(_) for _ in new_gurus]
    return new_gurus or None
