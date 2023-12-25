import pytest
from asyncpraw.models import WikiPage
from asyncpraw.reddit import Reddit, Subreddit

from data.consts import EPISODES_WIKI, GURU_SUB, TEST_SUB, TEST_WIKI
from gurupod.redditbot.managers import reddit_cm, subreddit_cm, wiki_page_cm
from gurupod.redditbot.subred import submission_in_stream_by_id, edit_reddit_wiki, submit_episode_subreddit
from gurupod.writer import RWikiWriter


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
async def test_edit_wiki(markup_sample, random_episode_validated, episodes_weird):
    async with wiki_page_cm(GURU_SUB, TEST_WIKI) as wiki:
        wiki: WikiPage = wiki
        await edit_reddit_wiki("", wiki)
        await wiki.load()
        assert wiki.content_md == ""

        # writer = RWikiWriter([random_episode_validated])
        writer = RWikiWriter(episodes_weird)
        markup = writer.write_many()

        await edit_reddit_wiki(markup, wiki)
        await wiki.load()
        print(f"http://reddit.com/r/{GURU_SUB}/wiki/{TEST_WIKI}")
        # assert wiki.content_md == markup_sample

        # cl = await edit_reddit_wiki('', wiki)


# @pytest.mark.skip(reason="Writes to web")
@pytest.mark.asyncio
async def test_post_and_get_submission_by_id(random_episode_validated):
    async with subreddit_cm(TEST_SUB) as subreddit:
        posted = await submit_episode_subreddit(random_episode_validated, subreddit)
        found = await submission_in_stream_by_id(posted.id, subreddit)
        assert found == posted


@pytest.mark.skip(reason="just for output")
@pytest.mark.asyncio
async def test_get_wiki_md():
    async with wiki_page_cm(page_name=EPISODES_WIKI) as wiki:
        content = wiki.content_md
        with open("wiki.md", "w", encoding="utf8") as f:
            f.write(content)


# @pytest.mark.asyncio
# async def test_streamer():
#     async with subreddit_cm(TEST_SUB) as subreddit:
#         res = await run_jobs(subreddit, job=get_guru_threads, dispatch_timeout=5)
#         ...
