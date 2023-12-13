import asyncio
from asyncio import create_task
from typing import AsyncGenerator

from asyncpraw.reddit import Submission, Subreddit

from data.consts import GURU_SUB
from data.gurunames import GURUS
from gurupod.redditbot.reddit import SubmissionFlairs, apply_flair_one, subreddit_cm


async def _find_jobs(subreddit: Subreddit, tags=GURUS) -> AsyncGenerator[Submission, list[str]]:
    async for submission in subreddit.stream.submissions():
        print("Starting stream...")
        found_tags = []
        for found in tags:
            if found in submission.title:
                print(f'\n{submission.title} contains {found.upper()}')
                found_tags.append(found)
        if found_tags:
            yield submission, found_tags


async def _prepare_jobs(subreddit: Subreddit) -> AsyncGenerator[SubmissionFlairs, None]:
    async for submission, flairs in _find_jobs(subreddit, tags=GURUS):
        gf = SubmissionFlairs(submission, flairs)
        yield gf


async def _dispatcher(subreddit: Subreddit, queue: asyncio.Queue, job=apply_flair_one,
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
    queue = asyncio.Queue()
    workers = [create_task(_worker(queue)) for _ in range(5)]
    dispatcher = create_task(_dispatcher(subreddit, queue, job=job))

    try:
        await asyncio.wait([dispatcher], timeout=dispatch_timeout)
    except asyncio.TimeoutError:
        print("Timeout")
    finally:
        for worker in workers:
            worker.cancel()
        dispatcher.cancel()
        await asyncio.gather(*workers, dispatcher, return_exceptions=True)


async def main():
    async with subreddit_cm(GURU_SUB) as subreddit:
        await do_jobs(subreddit, job=apply_flair_one, dispatch_timeout=30)

        if __name__ == '__main__':
            asyncio.run(main())
