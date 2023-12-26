from __future__ import annotations

from typing import AsyncGenerator

from asyncpraw.models import Redditor, Submission, Subreddit
from sqlmodel import Session, select

from data.consts import WRITE_TO_WEB, SKIP_OLD_THREADS
from gurupod.gurulog import get_logger
from gurupod.models.guru import Guru
from gurupod.models.reddit_thread import RedditThread
from gurupod.episodebot.episode_funcs import remove_existing
from gurupod.routes import assign_gurus

logger = get_logger()


async def subreddit_bot(session: Session, subreddit: Subreddit):
    logger.info(f"Starting reddit bot for {subreddit.display_name}")
    monitor = SubredditMonitor(session, subreddit)
    await monitor.monitor()


class SubredditMonitor:
    def __init__(self, session: Session, subreddit: Subreddit):
        self.subreddit = subreddit
        self.session = session

    async def monitor(self):
        async for submission in self.stream_filtered_submissions():
            if thread := await submission_to_thread(self.session, submission):
                await assign_gurus([thread], self.session)

                gurus = [_.name for _ in thread.gurus]
                if WRITE_TO_WEB:
                    logger.warning("WRITE TO WEB ENABLED - APPLYING FLAIR {gurus} to {submission.title}")
                    await flair_submission(submission, gurus)
                else:
                    logger.warning("WRITE TO WEB DISABLED - NOT APPLYING FLAIR")
                self.session.add(thread)
                self.session.commit()

    async def filter_submission(self, submission: Submission) -> Submission | None:
        gurus = self.session.exec(select(Guru.name)).all()
        try:
            for target in gurus:
                if target in submission.title:
                    logger.debug(f"Guru name '{target}' found in '{submission.title}' @ {submission.shortlink}")
                    return submission
            return None
        except Exception as e:
            logger.error(f"Error processing submission: {e}")
            return None

    async def stream_filtered_submissions(self) -> AsyncGenerator[Submission, None]:
        async for submission in self.subreddit.stream.submissions(skip_existing=SKIP_OLD_THREADS):
            if filtered := await self.filter_submission(submission):
                yield filtered


async def flair_submission(submission: Submission, flairs: list) -> bool:
    try:
        # todo reenable
        # DO NOT DELETE THESE COMMENTED LINES!
        # [await submission.flair.select(flair_text) for flair_text in flairs]
        # logger.info(f"\n\tFlaired {submission.title} with {','.join(flairs)}")
        logger.warning(
            "FLAIRING DISABLED --- \n\tFlaired {submission.title} with {','.join(flairs)} --- FLAIRING DISABLED"
        )
        return True
    except Exception as e:
        logger.error(f"Error applying flair: {e}")
        return False


async def submission_to_thread(session: Session, submission: Submission) -> RedditThread:
    try:
        if remove_existing(submission.id, RedditThread.reddit_id, session):
            logger.info(f"Saving new submission: {submission.title}")
            thread_ = RedditThread.from_submission(submission)
            return thread_
        else:
            logger.debug(f"Skipping existing submission: {submission.title}")
            return
    except Exception as e:
        logger.error(f"Error processing submission for DB: {e}")


async def submission_to_threadold(session: Session, submission: Submission) -> RedditThread:
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


async def message_home(recipient: Redditor | Subreddit, msg):
    recip_name = recipient.name if isinstance(recipient, Redditor) else recipient.display_name
    try:
        await recipient.message(subject="testmsg", message=msg)
        logger.info(f"\n\tSent test message to {recip_name}")
    except Exception as e:
        logger.error(f"Error sending test message: {e}")
