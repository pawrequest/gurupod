from loguru import logger
import asyncio
from asyncio import create_task
from typing import AsyncGenerator, NamedTuple

from asyncpraw.reddit import Submission, Subreddit

from data.consts import GURU_SUB
from data.gurunames import GURUS
from gurupod.redditbot.managers import subreddit_cm


class SubmissionFlairs(NamedTuple):
    submission: Submission
    flairs: list[str]

    def __bool__(self):
        return bool(self.flairs)


async def print_flair(sub_flairs: SubmissionFlairs) -> bool:
    try:
        for guru in sub_flairs.flairs:
            # todo turn back on
            # await sub_flairs.submission.flair.select(GURU_FLAIR_ID, text=guru)
            logger.info(f'\n{guru.upper()} tagged in "{sub_flairs.submission.title}"')
        return True
    except Exception as e:
        logger.error(f'error applying flair: {e}')
        return False


async def _find_flairables(subreddit: Subreddit, tags=GURUS) -> AsyncGenerator[
    Submission, list[str]]:
    async for submission in subreddit.stream.submissions():
        found_tags = []
        for guru in tags:
            if guru in submission.title:
                logger.info(f'\n{guru.upper()} found in {submission.title}')
                found_tags.append(guru)
        if found_tags:
            yield submission, found_tags


async def _flair_streamer(subreddit: Subreddit) -> AsyncGenerator[SubmissionFlairs, None]:
    logger.info("Starting stream...")
    async for submission, flairs in _find_flairables(subreddit, tags=GURUS):
        gf = SubmissionFlairs(submission, flairs)
        logger.info(f'Found flairs: {gf.flairs}')
        yield gf


async def doneworkerbee(queue: asyncio.Queue):
    while True:
        task = await queue.get()
        try:
            await task
        except Exception as e:
            logger.error(f"Task raised an exception: {e}")
        finally:
            queue.task_done()


async def done__flair_dispatch(subreddit: Subreddit, queue: asyncio.Queue, queue_timeout=None):
    async for sub_flairs in _flair_streamer(subreddit):
        task = create_task(print_flair(sub_flairs))
        await queue.put(task)
    await asyncio.wait_for(queue.join(), timeout=queue_timeout)


async def flair_submissions(subreddit: Subreddit, dispatch_timeout: int or None = 30):
    queue = asyncio.Queue()
    workers = [create_task(doneworkerbee(queue)) for _ in range(5)]
    dispatcher = create_task(done__flair_dispatch(subreddit, queue))

    try:
        await asyncio.wait([dispatcher], timeout=dispatch_timeout)
    except asyncio.TimeoutError:
        logger.warning("Timeout")
    finally:
        for worker in workers:
            worker.cancel()
        dispatcher.cancel()
        await asyncio.gather(*workers, dispatcher, return_exceptions=True)


async def main():
    async with subreddit_cm(GURU_SUB) as subreddit:
        await flair_submissions(subreddit, dispatch_timeout=30)


if __name__ == '__main__':
    asyncio.run(main())
