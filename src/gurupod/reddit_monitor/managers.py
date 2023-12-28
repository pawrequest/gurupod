from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from asyncpraw.reddit import Reddit, Subreddit

from data.consts import CLIENT_ID, CLIENT_SEC, REDDIT_TOKEN, REDIRECT, TEST_SUB, USER_AGENT
from gurupod.gurulog import get_logger

logger = get_logger()

if TYPE_CHECKING:
    pass


@asynccontextmanager
async def reddit_cm() -> Reddit:
    try:
        async with Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SEC,
            user_agent=USER_AGENT,
            redirect_uri=REDIRECT,
            refresh_token=REDDIT_TOKEN,
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
async def wiki_page_cm(subreddit: Subreddit, page_name: str):
    try:
        wiki_page = await subreddit.wiki.get_page(page_name)
        yield wiki_page
    except Exception as e:
        logger.error(f"error in wiki_page_cm: {e}")
        raise e
    finally:
        ...
