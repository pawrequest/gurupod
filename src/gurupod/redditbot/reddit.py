from __future__ import annotations

from contextlib import asynccontextmanager
from typing import NamedTuple, TYPE_CHECKING

from asyncpraw.models import WikiPage
from asyncpraw.reddit import Reddit, Submission, Subreddit

from data.consts import GURU_SUB, REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, \
    REDDIT_REF_TOK, REDIRECT, TEST_SUB, TEST_WIKI, USER_AGENT
from gurupod.writer import RWikiWriter, RPostWriter

if TYPE_CHECKING:
    from gurupod.models.episode import Episode


class SubmissionFlairs(NamedTuple):
    submission: Submission
    flairs: list[str]

    def __bool__(self):
        return bool(self.flairs)


@asynccontextmanager
async def reddit_cm() -> Reddit:
    try:

        async with Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SEC,
                user_agent=USER_AGENT,
                redirect_uri=REDIRECT,
                refresh_token=REDDIT_REF_TOK
        ) as reddit:
            yield reddit
    finally:
        await reddit.close()


@asynccontextmanager
async def subreddit_cm(sub_name: str = None) -> Subreddit:
    if sub_name is None:
        sub_name = TEST_SUB
    async with reddit_cm() as reddit:
        subreddit: Subreddit = await reddit.subreddit(sub_name)
        try:
            yield subreddit
        finally:
            await reddit.close()


@asynccontextmanager
async def wiki_page_cm(sub_name: str | None = None, page_name: str | None = None):
    if sub_name is None:
        sub_name = GURU_SUB
    if page_name is None:
        page_name = TEST_WIKI
    async with subreddit_cm(sub_name=sub_name) as subreddit:
        wiki_page = await subreddit.wiki.get_page(page_name)
        try:
            yield wiki_page
        except Exception as e:
            print(f'error in wiki_page_cm: {e}')
            raise e
        finally:
            ...


async def title_in_subreddit(title, subreddit: Subreddit) -> Submission:
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if title in submission.title:
            return submission


async def submission_in_stream_by_id(submission_id: str, subreddit: Subreddit) -> Submission:
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if submission_id == submission.id:
            return submission


async def submit_episode_subreddit(episode: Episode, sub_reddit: Subreddit):
    title = f'NEW EPISODE: {episode.name}'
    writer = RPostWriter([episode])
    text = writer.write_many()
    submission: Submission = await sub_reddit.submit(title, selftext=text)
    return submission


async def edit_reddit_wiki(markup, wiki: WikiPage):
    await wiki.edit(content=markup)
    res = {
        'wiki': wiki.__str__,
        'revision_by': str(wiki.revision_by),
        'revision_date': wiki.revision_date,
        'revision': wiki.revision_id,
    }
    return res


async def apply_flair_one(sub_flairs: SubmissionFlairs) -> bool:
    try:
        for guru in sub_flairs.flairs:
            # todo turn back on
            # await sub_flairs.submission.flair.select(GURU_FLAIR_ID, text=guru)
            print(f'\n{guru.upper()} tagged in "{sub_flairs.submission.title}"')
        return True
    except Exception as e:
        print(f'error applying flair: {e}')
        return False
