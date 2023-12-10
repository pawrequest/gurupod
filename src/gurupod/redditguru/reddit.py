from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, NamedTuple, TYPE_CHECKING

from asyncpraw.models import WikiPage
from asyncpraw.reddit import Reddit, Submission, Subreddit

from data.consts import DTG_SUB, GURU_FLAIR_ID, REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, \
    REDDIT_REF_TOK, REDIRECT, TEST_SUB, TEST_WIKI, USER_AGENT
from data.gurunames import GURUS
from gurupod.markupguru.markup_writer import episodes_reddit

if TYPE_CHECKING:
    from gurupod.models.episode import Episode


class GuruFlairs(NamedTuple):
    submission: Submission
    gurus: list[str]


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
        reddit.close()


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
        sub_name = DTG_SUB
    if page_name is None:
        page_name = TEST_WIKI
    async with subreddit_cm(sub_name=sub_name) as subreddit:
        wiki_page = await subreddit.wiki.get_page(page_name)
        try:
            yield wiki_page
        finally:
            ...


async def find_title_in_subreddit_stream(title, subreddit: Subreddit):
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if title in submission.title:
            return submission


async def find_submission_in_subreddit_stream(submission_id: str, subreddit: Subreddit):
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if submission_id == submission.id:
            return submission


async def guru_flair(guruflairs: list[GuruFlairs]):
    for gf in guruflairs:
        for guru in gf.gurus:
            await gf.submission.flair.select(GURU_FLAIR_ID, text=guru)
            print(f'\n{guru.upper()} tagged in "{gf.submission.title}"')
            ...
    return True


async def submissions_with_gurus_in_title(subreddit: Subreddit, gurus=GURUS) -> AsyncGenerator[
    Submission, list[str]]:
    async for submission in subreddit.stream.submissions():
        found_gurus = []
        for guru in gurus:
            if guru in submission.title:
                print(f'\n{guru.upper()} found in {submission.title}')
                found_gurus.append(guru)
        if found_gurus:
            yield submission, found_gurus


async def get_one_submission_with_gurus_in_title(subreddit: Subreddit, gurus=GURUS) -> GuruFlairs:
    async for submission in subreddit.stream.submissions():
        found_gurus = []
        for guru in gurus:
            if guru in submission.title:
                print(f'\n{guru.upper()} found in {submission.title}')
                found_gurus.append(guru)
        if found_gurus:
            return GuruFlairs(submission, found_gurus)


async def submit_episode_subreddit(episode: Episode, sub_reddit: Subreddit):
    title = f'NEW EPISODE: {episode.name}'
    text = episodes_reddit([episode])
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


if __name__ == '__main__':
    # guru_flair()
    # submit_episiode()
    ...
