import pytest
from asyncpraw.models import WikiPage
from asyncpraw.reddit import Reddit, Subreddit

from data.consts import GURU_SUB, TEST_SUB, TEST_WIKI
from gurupod.redditguru.reddit import edit_reddit_wiki, reddit_cm, submission_id_in_subreddit, \
    submit_episode_subreddit, subreddit_cm, wiki_page_cm


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


@pytest.mark.skip(reason="Writes to web")
@pytest.mark.asyncio
async def test_edit_wiki(markup_sample):
    async with wiki_page_cm(GURU_SUB, TEST_WIKI) as wiki:
        await edit_reddit_wiki('', wiki)
        await wiki.load()
        assert wiki.content_md == ''

        await edit_reddit_wiki(markup_sample, wiki)
        await wiki.load()
        assert wiki.content_md == markup_sample

        cl = await edit_reddit_wiki('', wiki)


@pytest.mark.skip(reason="Writes to web")
@pytest.mark.asyncio
async def test_post_to_subreddit(episode_validated_fxt):
    async with subreddit_cm(TEST_SUB) as subreddit:
        posted = await submit_episode_subreddit(episode_validated_fxt, subreddit)
        found = await submission_id_in_subreddit(posted.id, subreddit)
        assert found == posted
