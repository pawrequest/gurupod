import asyncio

import pytest
from asyncpraw.models import WikiPage
from asyncpraw.reddit import Reddit, Subreddit

from data.consts import DTG_SUB, TEST_SUB, TEST_WIKI
from data.gurunames import GURUS
from gurupod.redditguru.reddit import edit_reddit_wiki, \
    find_submission_in_subreddit_stream, \
    get_one_submission_with_gurus_in_title, guru_flair, reddit_cm, \
    submissions_with_gurus_in_title, submit_episode_subreddit, \
    subreddit_cm, wiki_page_cm


@pytest.mark.asyncio
async def test_reddit_cm():
    async with reddit_cm() as reddit:
        assert isinstance(reddit, Reddit)


@pytest.mark.asyncio
async def test_subred_cm():
    async with subreddit_cm() as subreddit:
        assert isinstance(subreddit, Subreddit)


@pytest.mark.asyncio
async def test_wiki_cm():
    async with wiki_page_cm() as wiki:
        assert isinstance(wiki, WikiPage)


@pytest.mark.asyncio
async def test_edit_wiki(markup_sample):
    async with wiki_page_cm(DTG_SUB, TEST_WIKI) as wiki:
        await edit_reddit_wiki('', wiki)
        await wiki.load()
        assert wiki.content_md == ''

        await edit_reddit_wiki(markup_sample, wiki)
        await wiki.load()
        assert wiki.content_md == markup_sample

        cl = await edit_reddit_wiki('', wiki)


@pytest.mark.asyncio
async def test_post_to_subreddit(episode_validated_fxt):
    async with subreddit_cm(TEST_SUB) as subreddit:
        posted = await submit_episode_subreddit(episode_validated_fxt, subreddit)
        found = await find_submission_in_subreddit_stream(posted.id, subreddit)
        assert found == posted


@pytest.mark.asyncio
async def test_submissions_with_gurus_in_title():
    async def consume_submissions(submissions):
        async for sub, gurus in submissions:
            ...

    async with subreddit_cm(DTG_SUB) as subreddit:
        subsy = submissions_with_gurus_in_title(subreddit, gurus=GURUS)
        try:
            await asyncio.wait_for(consume_submissions(subsy), timeout=10)

        except asyncio.TimeoutError:
            print("Timeout reached")
        finally:
            await subsy.aclose()
            ...


@pytest.mark.asyncio
async def test_apply_flair_one():
    async with subreddit_cm(DTG_SUB) as subreddit:
        gf = await get_one_submission_with_gurus_in_title(subreddit, gurus=GURUS)
        res = await guru_flair([gf])
        ...
