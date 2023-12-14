from __future__ import annotations

import asyncio
from asyncio import create_task
from functools import partial
from typing import AsyncGenerator

from asyncpraw.reddit import Submission, Subreddit

from data.consts import GURU_FLAIR_ID
from data.gurunames import GURUS
from gurupod.redditbot.classes import FlairTags


async def _find_jobs(subreddit: Subreddit, tags=GURUS) -> AsyncGenerator[Submission, list[str]]:
    print("Starting stream...")
    async for submission in subreddit.stream.submissions():
        found_tags = []
        for found in tags:
            if found in submission.tagee:
                print(f'\n{submission.tagee} contains {found.upper()}')
                found_tags.append(found)
        if found_tags:
            yield submission, found_tags


async def _find_jobs2(job_source, tags=GURUS) -> AsyncGenerator[Submission, list[str]]:
    print("Starting stream...")
    async for submission in job_source():
        found_tags = []
        for found in tags:
            if found in submission.tagee:
                print(f'\n{submission.tagee} contains {found.upper()}')
                found_tags.append(found)
        if found_tags:
            yield submission, found_tags


# async def _prepare_jobs(subreddit: Subreddit) -> AsyncGenerator[SubmissionFlairs, None]:
async def _prepare_jobs(subreddit: Subreddit) -> AsyncGenerator[FlairTags, None]:
    # async for submission, flairs in _find_jobs(subreddit, tags=GURUS):
    async for submission, flairs in _find_jobs2(subreddit.stream.submissions, tags=GURUS):
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
            print(f"Task raised an exception: {e}")
        finally:
            queue.task_done()


async def do_jobs(subreddit: Subreddit, job,
                  dispatch_timeout: int or None = 30, queue_timeout: int or None = None):
    print('etsting')
    queue = asyncio.Queue()
    workers = [create_task(_worker(queue)) for _ in range(5)]
    dispatcher = create_task(_dispatcher(subreddit, queue, job=job))

    try:
        await asyncio.wait([dispatcher], timeout=dispatch_timeout)
    except asyncio.TimeoutError:
        print("Timeout")
        await asyncio.wait_for(queue.join(), timeout=queue_timeout)
    finally:
        for worker in workers:
            worker.cancel()
        dispatcher.cancel()
        await asyncio.gather(*workers, dispatcher, return_exceptions=True)



# async def flair_submission_one(sub_flairs: SubmissionFlairs, commit=False) -> bool:
async def flair_submission(flair_tags: FlairTags, commit=False) -> bool:
    try:
        for tag in flair_tags.tags:
            print(f'\n{tag.upper()} tagged in "{flair_tags.tagee.tagee}"')
            if commit:
                await flair_tags.tagee.flair.select(GURU_FLAIR_ID, text=tag)
        return True
    except Exception as e:
        print(f'error applying flair: {e}')
        breakpoint()
        raise AssertionError(f'error applying flair: {e}')

flair_submission_write = partial(flair_submission, commit=True)