from __future__ import annotations

from typing import AsyncGenerator

from asyncpraw.reddit import Submission

from data.gurunames import GURUS
from gurupod.gurulog import get_logger
from gurupod.redditbot.managers import subreddit_cm

logger = get_logger()


async def filter_submission(submission: Submission, filter_sequence=GURUS) -> Submission | None:
    try:
        for target in filter_sequence:
            if target in submission.title:
                logger.info(f"Guru name '{target}' found in '{submission.title}' @ {submission.shortlink}")
                return submission
        return None
    except Exception as e:
        logger.error(f"Error processing submission: {e}")
        return None


async def submission_monitor(subreddit_name: str, timeout: int = None) -> AsyncGenerator[Submission, None]:
    async with subreddit_cm(subreddit_name) as subreddit:
        logger.info(f"Monitoring subreddit: {subreddit_name}")

        async for submission in subreddit.stream.submissions():
            logger.debug(f"New unfiltered submission: {submission.title}")
            if filtered := await filter_submission(submission):
                yield filtered
