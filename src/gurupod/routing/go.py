from typing import AsyncGenerator

from asyncpraw.models import Submission

from gurupod.gurulog import get_logger
from gurupod.redditbot.managers import subreddit_cm

logger = get_logger()


class SubmissionMonitor:
    def __init__(self, subreddit_name: str, filter_sequence):
        self.subreddit_name = subreddit_name
        self.filter_sequence = filter_sequence

    async def filter_submission(self, submission: Submission) -> Submission | None:
        try:
            for target in self.filter_sequence:
                if target in submission.title:
                    logger.info(f"Guru name '{target}' found in '{submission.title}' @ {submission.shortlink}")
                    return submission
            return None
        except Exception as e:
            logger.error(f"Error processing submission: {e}")
            return None

    async def stream_filtered_submissions(self) -> AsyncGenerator[Submission, None]:
        async with subreddit_cm(self.subreddit_name) as subreddit:
            logger.info(f"Monitoring subreddit: {self.subreddit_name}")

            async for submission in subreddit.stream.submissions():
                logger.debug(f"New unfiltered submission: {submission.title}")
                if filtered := await self.filter_submission(submission):
                    yield filtered
