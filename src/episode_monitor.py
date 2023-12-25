import asyncio

from asyncpraw.models import Redditor, Subreddit

from data.consts import WRITE_TO_WEB
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode
from gurupod.redditbot.monitor import message_home
from gurupod.redditbot.subred import reddit_episode_submitted_msg, submit_episode_subreddit
from gurupod.routing.episode_routes import fetch

logger = get_logger()


async def episode_monitor(session, subreddit, interval, recipient: Redditor | Subreddit) -> None:
    while True:
        await scrape_import_and_post_episode(session, subreddit, recipient)
        logger.info(f"Sleeping for {interval} seconds")
        await asyncio.sleep(interval)


async def scrape_import_and_post_episode(session, subreddit, recipient: Redditor | Subreddit) -> None:
    if neweps := await fetch(session=session):
        logger.info(f"Found {len(neweps.episodes)} new episodes")
        for ep in neweps.episodes:
            # logger.info(f"Fetched new episode: {ep.title}")
            await process_new_episode(ep, recipient, subreddit)
    else:
        logger.info("No new episodes found")


async def process_new_episode(ep: Episode, recipient, subreddit) -> None:
    if WRITE_TO_WEB:
        submitted = await submit_episode_subreddit(ep, subreddit)
        message_txt = reddit_episode_submitted_msg(submitted, ep)
        await message_home(recipient, message_txt)
    else:
        logger.warning("WRITE TO WEB DISABLED - NOT PROCESSING NEW EPISODE")
