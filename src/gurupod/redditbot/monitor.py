from __future__ import annotations

from typing import AsyncGenerator

from asyncpraw.models import Submission, Subreddit
from sqlmodel import Session, select

from gurupod.gurulog import get_logger
from gurupod.models.guru import Guru
from gurupod.models.reddit_model import RedditThread
from gurupod.routing.episode_funcs import remove_existing
from gurupod.routing.episode_routes import assign_gurus

logger = get_logger()


class SubredditMonitor:
    def __init__(self, session: Session, subreddit: Subreddit):
        self.subreddit = subreddit
        self.session = session

    async def monitor(self):
        async for submission in self.stream_filtered_submissions():
            if thread := await submission_to_thread(self.session, submission):
                await assign_gurus([thread], self.session)

                gurus = [_.name for _ in thread.gurus]
                await flair_submission(submission, gurus)
                self.session.add(thread)
                self.session.commit()

    async def filter_submission(self, submission: Submission) -> Submission | None:
        gurus = self.session.exec(select(Guru.name)).all()
        try:
            for target in gurus:
                if target in submission.title:
                    logger.info(f"Guru name '{target}' found in '{submission.title}' @ {submission.shortlink}")
                    return submission
            return None
        except Exception as e:
            logger.error(f"Error processing submission: {e}")
            return None

    async def stream_filtered_submissions(self) -> AsyncGenerator[Submission, None]:
        logger.info(f"Monitoring subreddit: {self.subreddit.display_name}")

        async for submission in self.subreddit.stream.submissions():
            if filtered := await self.filter_submission(submission):
                yield filtered


async def flair_submission(submission: Submission, flairs: list) -> bool:
    try:
        # todo reenable
        # [await submission.flair.select(flair_text) for flair_text in flairs]
        logger.info(f"Flaired {submission.title} with {','.join(flairs)}")
        return True
    except Exception as e:
        logger.error(f"Error applying flair: {e}")
        return False


async def submission_to_thread(session: Session, submission: Submission) -> RedditThread:
    try:
        if not remove_existing([submission.id], RedditThread.reddit_id, session):
            logger.debug(f"Skipping existing submission: {submission.title}")
            return
        else:
            logger.info(f"Saving new submission: {submission.title}")
            thread_ = RedditThread.from_submission(submission)

            return thread_
    except Exception as e:
        logger.error(f"Error processing submission for DB: {e}")
