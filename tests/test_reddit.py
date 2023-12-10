from contextlib import asynccontextmanager

import pytest
from asyncpraw.models import WikiPage
from asyncpraw.reddit import Reddit, Subreddit

from gurupod.redditguru.reddit import reddit_

@asynccontextmanager
async def reddit_fxt():
    reddit_instance = await reddit_()
    try:
        yield reddit_instance
    finally:
        await reddit_instance.close()

@pytest.fixture(scope="function")
async def subreddit_fxt():
    async with reddit_fxt() as reddit:
        return await reddit.subreddit('test')

@pytest.fixture(scope="function")
async def wiki_fxt(subreddit_fxt):
    subreddit = await subreddit_fxt
    return await subreddit.wiki.get_page('gurus')
#
# @asynccontextmanager
# async def reddit_fxt():
#     reddit_instance = await reddit_()
#     try:
#         yield reddit_instance
#     finally:
#         await reddit_instance.close()
#
#
# @pytest.mark.asyncio
# @pytest.fixture(scope="function")
# async def subreddit_fxt():
#     async with reddit_fxt() as reddit:
#         subreddit_instance = await reddit.subreddit('test')
#         assert isinstance(subreddit_instance, Subreddit)
#         return subreddit_instance
#
#
# @pytest.mark.asyncio
# @pytest.fixture(scope="function")
# async def wiki_fxt(subreddit_fxt):
#     subreddit = await subreddit_fxt
#     wiki_instance = await subreddit.wiki.get_page('test')
#     assert isinstance(wiki_instance, WikiPage)
#     return wiki_instance


@pytest.mark.asyncio
async def test_wiki_fxt(wiki_fxt):
    wiki = await wiki_fxt
    assert isinstance(wiki, WikiPage)


@pytest.mark.asyncio
async def test_reddit_fxt():
    async with reddit_fxt() as reddit:
        assert isinstance(reddit, Reddit)


@pytest.mark.asyncio
async def test_subreddit_fxt(subreddit_fxt):
    subreddit = await subreddit_fxt
    assert isinstance(subreddit, Subreddit)

# @pytest.mark.asyncio
# async def test_reddit_edit_wiki(wiki_testing, markup_sample):
#     wiki = await wiki_testing
#     res = await edit_reddit_wiki(markup_sample, wiki)
#     ...
#
# @pytest.mark.asyncio
# async def test_submit_reddit_episode(subreddit_testing, episode_validated_fxt):
#     subreddit = await subreddit_testing
#     episode = episode_validated_fxt
#     res = await submit_episode_subreddit(episode, subreddit)
#     ...
