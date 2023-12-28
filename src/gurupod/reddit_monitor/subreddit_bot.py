from __future__ import annotations

from typing import AsyncGenerator, Sequence

from asyncpraw.models import Redditor, Submission, Subreddit, WikiPage
from sqlmodel import Session, select

from data.consts import DO_FLAIR, SKIP_OLD_THREADS
from gurupod.gurulog import get_logger
from gurupod.models.episode import EpisodeBase
from gurupod.models.guru import Guru
from gurupod.models.reddit_thread import RedditThread
from gurupod.podcast_monitor.writer import RPostWriter

logger = get_logger()


async def subreddit_bot(session: Session, subreddit: Subreddit):
    bot = SubredditBot(session, subreddit)
    await bot.monitor()


class SubredditBot:
    def __init__(self, session: Session, subreddit: Subreddit):
        self.subreddit = subreddit
        self.session = session

    async def monitor(self):
        logger.info(f"DecodeTheBot monitoring r/{self.subreddit.display_name} for guru related threads")

        sub_stream = self.submission_stream()
        new = filter_existing_submissions(sub_stream, self.session)
        subs_and_gurus = subs_with_gurus(new, self.session)
        reddit_threads = subs_and_gurus_to_thread(subs_and_gurus)
        async for reddit_thread in reddit_threads:
            self.session.add(reddit_thread)
            self.session.commit()
            if DO_FLAIR:
                logger.warning("DO FLAIR ENABLED - APPLYING FLAIR {gurus} to {submission.title}")
                await flair_submission(reddit_thread.submission, reddit_thread.gurus)
            else:
                logger.warning("DO FLAIR DISABLED - NOT APPLYING FLAIR")

    async def submission_stream(self) -> AsyncGenerator[Submission, None]:
        async for submission in self.subreddit.stream.submissions(skip_existing=SKIP_OLD_THREADS):
            yield submission


async def flair_submission(submission: Submission, flairs: list) -> bool:
    try:
        # todo this probably doesnt work? need to use the flairid....
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
        logger.error(f"Error Turning Submission into RedditThread {e}")


async def subs_and_gurus_to_thread(
    sub_stream: AsyncGenerator[tuple[Submission, Sequence[Guru]], None],
) -> AsyncGenerator[RedditThread, None]:
    async for submission, gurus in sub_stream:
        if thread_ := await submission_to_thread(submission):
            thread_.gurus.extend(gurus)
            logger.info(
                f'New Guru Thread: {[_.name for _ in thread_.gurus]} in "{thread_.title}" @ {thread_.shortlink}'
            )
            yield thread_


async def subs_to_threads(
    sub_stream: AsyncGenerator[Submission, None],
) -> AsyncGenerator[RedditThread, None]:
    async for submission in sub_stream:
        if thread_ := await submission_to_thread(submission):
            logger.info(f"Yielding new submission: {thread_.title} with {[_.name for _ in thread_.gurus]}")
            yield thread_


async def message_home(recipient: Redditor | Subreddit, msg):
    recip_name = recipient.name if isinstance(recipient, Redditor) else recipient.display_name
    try:
        await recipient.message(subject="testmsg", message=msg)
        logger.info(f"\n\tSent test message to {recip_name}")
    except Exception as e:
        logger.error(f"Error sending test message: {e}")


async def subs_with_gurus(
    submission_stream: AsyncGenerator[Submission, None], session: Session
) -> AsyncGenerator[tuple[Submission, Sequence[Guru]], None]:
    tag_models = session.exec(select(Guru)).all()
    async for submission in submission_stream:
        if matched_tag_models := [_ for _ in tag_models if _.name in submission.title]:
            yield submission, matched_tag_models


async def edit_reddit_wiki(markup: str, wiki: WikiPage):
    await wiki.edit(content=markup)
    res = {
        "wiki": wiki.__str__,
        "revision_by": str(wiki.revision_by),
        "revision_date": wiki.revision_date,
        "revision": wiki.revision_id,
    }
    return res


async def submit_episode_subreddit(episode: EpisodeBase, sub_reddit: Subreddit) -> Submission:
    try:
        title = f"NEW EPISODE: {episode.title}"
        writer = RPostWriter(episode)
        text = writer.write_many()
        submission: Submission = await sub_reddit.submit(title, selftext=text)
        logger.info(f"\n\tSubmitted {episode.title} to {sub_reddit.display_name}: {submission.shortlink}")

        return submission
    except Exception as e:
        logger.error(f"Error submitting episode: {e}")
        return None