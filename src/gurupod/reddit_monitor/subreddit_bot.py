from __future__ import annotations

from typing import AsyncGenerator

from asyncpraw.models import Subreddit, WikiPage
from asyncpraw.reddit import Reddit, Submission
from sqlmodel import Session, select

from gurupod.core.consts import DO_FLAIR, GURU_FLAIR_ID, SKIP_OLD_THREADS, SUB_TO_MONITOR, SubmissionGurus
from loguru import logger
from gurupod.models.guru import Guru
from gurupod.models.reddit_thread import RedditThread


class SubredditMonitor:
    def __init__(self, session: Session, subreddit: Subreddit):
        self.subreddit = subreddit
        self.session = session

    @classmethod
    async def from_config(cls, session: Session, reddit: Reddit):
        subreddit = await reddit.subreddit(SUB_TO_MONITOR)
        return cls(session, subreddit)

    async def monitor(self):
        logger.info(
            f"Initialised - watching  http://reddit.com/r/{self.subreddit.display_name} for guru related threads",
            bot_name="Monitor",
        )

        sub_stream = self.subreddit.stream.submissions(skip_existing=SKIP_OLD_THREADS)
        new = self.filter_existing_submissions(sub_stream)
        subs_plus = self.subs_with_gurus(new)
        subs_threads = self.subs_plus_to_subs_threads(subs_plus)
        async for submission, reddit_thread in subs_threads:
            self.session.add(reddit_thread)
            self.session.commit()
            if DO_FLAIR:
                flair_names = [_.name for _ in submission.gurus]
                try:
                    await flair_submission(submission, flair_names)
                except Exception as e:
                    logger.error(f"Error applying flair: {e}", bot_name="Monitor")
            else:
                logger.warning("DO FLAIR DISABLED - NOT APPLYING FLAIR", bot_name="Monitor")

    async def subs_plus_to_subs_threads(
        self,
        sub_stream: AsyncGenerator[SubmissionGurus, None],
    ) -> AsyncGenerator[tuple[SubmissionGurus, RedditThread], None]:
        async for submission in sub_stream:
            thread = await submission_to_thread(submission)
            thread.gurus.extend(submission.gurus)
            logger.info(
                f'New Guru Thread: {[_.name for _ in thread.gurus]} in "{thread.title}" @ {thread.shortlink}',
                bot_name="Monitor",
            )
            yield submission, thread

    def submission_exists(self, submission: Submission) -> bool:
        existing_thread = self.session.exec(
            select(RedditThread).where((RedditThread.reddit_id == submission.id))
        ).first()
        return existing_thread is not None

    async def filter_existing_submissions(
        self, sub_stream: AsyncGenerator[Submission, None]
    ) -> AsyncGenerator[Submission, None]:
        async for submission in sub_stream:
            if not self.submission_exists(submission):
                yield submission

    async def subs_with_gurus(
        self, submission_stream: AsyncGenerator[Submission, None]
    ) -> AsyncGenerator[SubmissionGurus, None]:
        # todo find a way to update gurulist without constantly asking db.. signal?
        async for submission in submission_stream:
            tag_models = self.session.exec(select(Guru)).all()
            if matched_tag_models := [_ for _ in tag_models if _.name.lower() in submission.title.lower()]:
                submission.gurus = matched_tag_models
                yield submission
                # yield submission, matched_tag_models


async def flair_submission(submission: Submission, flairs: list) -> bool:
    try:
        for flair in flairs:
            try:
                # whats this pycharm error Fixture 'submission.flair.select' is not requested by test functions or @pytest.mark.usefixtures marker
                await submission.flair.select(GURU_FLAIR_ID, text=flair)
                logger.warning(f"Flaired {submission.title} with {flair}", bot_name="Monitor")
            except Exception as e:
                logger.error(f"Error applying flair: to {submission.title} {e}", bot_name="Monitor")
        return True
    except Exception as e:
        logger.error(f"Error applying flair: {e}", bot_name="Monitor")
        return False


async def submission_to_thread(submission: Submission) -> RedditThread:
    try:
        thread_ = RedditThread.from_submission(submission)
        return RedditThread.model_validate(thread_)
    except Exception as e:
        logger.error(f"Error Turning Submission into RedditThread {e}", bot_name="Monitor")


async def _edit_reddit_wiki(markup: str, wiki: WikiPage):
    await wiki.edit(content=markup)
    res = {
        "wiki": wiki.__str__,
        "revision_by": str(wiki.revision_by),
        "revision_date": wiki.revision_date,
        "revision": wiki.revision_id,
    }
    return res


# dont delete, good for testing
async def submission_in_stream_by_id(submission_id: str, subreddit: Subreddit) -> bool:
    async for submission in subreddit.stream.submissions():
        if submission_id == submission.id:
            return True


async def submission_in_stream_by_title(title, subreddit: Subreddit) -> bool:
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if title in submission.title:
            return True
