from __future__ import annotations
from gurupod.gurulog import logger

import asyncio
from asyncio import create_task
from functools import partial
from typing import AsyncGenerator

from asyncpraw.reddit import Submission, Subreddit

from data.consts import GURU_FLAIR_ID, GURU_SUB
from data.gurunames import GURUS
from gurupod.redditbot.classes import FlairTags
from gurupod.redditbot.managers import subreddit_cm


async def _find_jobs(job_source, tags=GURUS) -> AsyncGenerator[Submission, list[str]]:
    async for submission in job_source():
        found_tags = []
        for tag in tags:
            if tag in submission.title:
                found_tags.append(tag)
        if found_tags:
            yield submission, found_tags


async def _prepare_jobs(subreddit: Subreddit) -> AsyncGenerator[FlairTags, None]:
    logger.debug(f"Starting stream: {subreddit.display_name}")

    async for submission, flairs in _find_jobs(subreddit.stream.submissions, tags=GURUS):
        gf = FlairTags(submission, flairs)
        yield gf


async def _dispatcher(subreddit: Subreddit, queue: asyncio.Queue, job,
                      queue_timeout=None):
    async for sub_flairs in _prepare_jobs(subreddit):
        task = create_task(job(sub_flairs))
        await queue.put(task)
    await asyncio.wait_for(queue.join(), timeout=queue_timeout)


async def _worker(queue: asyncio.Queue):
    while True:
        task = await queue.get()
        try:
            await task
        except Exception as e:
            logger.error(f"Task raised an exception: {e}")
        finally:
            queue.task_done()


async def run_jobs(subreddit: Subreddit, job,
                   dispatch_timeout: int or None = 30, queue_timeout: int or None = None):
    queue = asyncio.Queue()
    workers = [create_task(_worker(queue)) for _ in range(5)]
    dispatcher = create_task(_dispatcher(subreddit, queue, job=job))

    try:
        await asyncio.wait([dispatcher], timeout=dispatch_timeout)
    except asyncio.TimeoutError:
        logger.warning("Timeout")
        await asyncio.wait_for(queue.join(), timeout=queue_timeout)
    finally:
        for worker in workers:
            worker.cancel()
        dispatcher.cancel()
        await asyncio.gather(*workers, dispatcher, return_exceptions=True)


async def flair_submission_write_optional(flair_tags: FlairTags, commit=False) -> bool:
    try:
        tags = flair_tags.tags
        logger.info(
            f'{', '.join(_.upper() for _ in tags)} found in "{flair_tags.tagee.title} @ {flair_tags.tagee.shortlink}"')
        for tag in tags:
            if commit:
                await flair_tags.tagee.flair.select(GURU_FLAIR_ID, text=tag)
                logger.info(f'flair applied: {tag}')
        return True
    except Exception as e:
        logger.error(f'error applying flair: {e}')
        return False


flair_submission_write = partial(flair_submission_write_optional, commit=True)


async def launch_monitor(subreddit_name=GURU_SUB, timeout: int or None = 30):
    async with subreddit_cm(subreddit_name) as subreddit_name:
        await run_jobs(subreddit_name, job=flair_submission_write_optional,
                       dispatch_timeout=timeout)
