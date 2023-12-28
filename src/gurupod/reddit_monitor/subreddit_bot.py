from __future__ import annotations

from typing import AsyncGenerator, Sequence

from asyncpraw.models import Subreddit, WikiPage
from asyncpraw.reddit import Submission
from sqlmodel import Session, select

from data.consts import DO_FLAIR, GURU_FLAIR_ID, SKIP_OLD_THREADS
from gurupod.gurulog import get_logger
from gurupod.models.guru import Guru
from gurupod.models.reddit_thread import RedditThread

logger = get_logger()


class SubredditMonitor:
    def __init__(self, session: Session, subreddit: Subreddit):
        self.subreddit = subreddit
        self.session = session

    async def monitor(self):
        logger.info(f"Monitor | watching http://reddit.com/r/{self.subreddit.display_name} for guru related threads")

        sub_stream = self.submission_stream()
        new = filter_existing_submissions(sub_stream, self.session)
        subs_and_gurus = subs_with_gurus(new, self.session)
        reddit_threads = subs_and_gurus_to_thread(subs_and_gurus)
        async for reddit_thread in reddit_threads:
            self.session.add(reddit_thread)
            self.session.commit()
            if DO_FLAIR:
                logger.warning("Monitor | DO FLAIR ENABLED - APPLYING FLAIR {gurus} to {submission.title}")
                await flair_submission(reddit_thread.submission, reddit_thread.gurus)
            else:
                logger.warning("Monitor | DO FLAIR DISABLED - NOT APPLYING FLAIR")

    async def submission_stream(self) -> AsyncGenerator[Submission, None]:
        async for submission in self.subreddit.stream.submissions(skip_existing=SKIP_OLD_THREADS):
            yield submission


async def flair_submission(submission: Submission, flairs: list) -> bool:
    try:
        # todo reenable
        # DO NOT DELETE THESE COMMENTED LINES!
        for flair in flairs:
            try:
                await submission.flair.select(GURU_FLAIR_ID, text=flair)
                logger.info(f"\n\tMonitor | Flaired {submission.title} with {flair}")
            except Exception as e:
                logger.error(f"Monitor | Error applying flair: to {submission.title} {e}")
        # [await submission.flair.select(GURU_FLAIR_ID, text=flair)for flair in flairs]
        logger.warning(
            "Monitor | FLAIRING DISABLED --- \n\tFlaired {submission.title} with {','.join(flairs)} --- FLAIRING DISABLED"
        )
        return True
    except Exception as e:
        logger.error(f"Monitor | Error applying flair: {e}")
        return False


def submission_exists(session, submission):
    existing_thread = session.exec(select(RedditThread).where((RedditThread.reddit_id == submission.id))).first()

    return existing_thread is not None


async def filter_existing_submissions(
    sub_stream: AsyncGenerator[Submission, None], session: Session
) -> AsyncGenerator[Submission, None]:
    async for submission in sub_stream:
        if not submission_exists(session, submission):
            yield submission


async def submission_to_thread(submission: Submission) -> RedditThread:
    try:
        thread_ = RedditThread.from_submission(submission)
        return thread_
    except Exception as e:
        logger.error(f"Monitor | Error Turning Submission into RedditThread {e}")


async def subs_and_gurus_to_thread(
    sub_stream: AsyncGenerator[tuple[Submission, Sequence[Guru]], None],
) -> AsyncGenerator[RedditThread, None]:
    async for submission, gurus in sub_stream:
        if thread_ := await submission_to_thread(submission):
            thread_.gurus.extend(gurus)
            logger.info(
                f'Monitor | New Guru Thread: {[_.name for _ in thread_.gurus]} in "{thread_.title}" @ {thread_.shortlink}'
            )
            yield thread_


async def subs_to_threads(
    sub_stream: AsyncGenerator[Submission, None],
) -> AsyncGenerator[RedditThread, None]:
    async for submission in sub_stream:
        if thread_ := await submission_to_thread(submission):
            logger.info(f"Monitor | Yielding new submission: {thread_.title} with {[_.name for _ in thread_.gurus]}")
            yield thread_


async def subs_with_gurus(
    submission_stream: AsyncGenerator[Submission, None], session: Session
) -> AsyncGenerator[tuple[Submission, Sequence[Guru]], None]:
    tag_models = session.exec(select(Guru)).all()
    async for submission in submission_stream:
        if matched_tag_models := [_ for _ in tag_models if _.name in submission.title]:
            yield submission, matched_tag_models


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
